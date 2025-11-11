import os
import sys
from importlib import reload
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qt_compat import QPushButton, QIcon, QSize, QFileDialog, QMessageBox, Qt
from main_window import ConverterUi
import slate_handler as slate
import converter_constants as constants
import file_handler as handler
import ffmpeg_handler as ffmpeg
from HANLib import init_logger

# Set Logger
log_name = "push_button"
log_dir = os.path.expanduser(r"~\Logs\ImgConverter")
log_path = str(Path(log_dir) / f"{log_name}.log")
LOGGER = init_logger.Logger(log_name, log_path)


class MenuButton(QPushButton):
    def __init__(self, image_name):
        super().__init__()
        self.create_button(image_name)

    def create_button(self, image_name):
        self.setFixedWidth(50)
        self.setFixedHeight(50)

        resource_path = Path(constants.RESOURCE_PATH)
        icon = QIcon(str(resource_path / image_name))
        self.setIcon(icon)
        self.setIconSize(QSize(20, 20))

        return self

class ButtonEventHandler(ConverterUi):
    def __init__(self, run_paths=None):
        super().__init__(run_paths)
        
        self.connect_buttons()

    def connect_buttons(self):
        self.add_img_btn.clicked.connect(self.add_images)
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.ascend_btn.clicked.connect(self.ascend_selected)
        self.descend_btn.clicked.connect(self.descend_selected)
        self.name_sort_btn.clicked.connect(self.sort_by_name)
        self.remove_btn.clicked.connect(self.remove_selected)
        self.save_dir_btn.clicked.connect(self.select_save_directory)
        self.convert_btn.clicked.connect(self.convert_images)
        self.slate_btn.clicked.connect(lambda: self.open_slate_settings(self.clicked_file_path))

    def open_slate_settings(self, file_path):
        reload(slate)
        checked_items = self.file_tree.get_checked_items()
        self.slate_window = slate.SlateHandler(file_path, checked_items)
        
    def add_images(self):
        img_ext = "*.jpg *.jpeg *.png *.bmp *.gif *.exr *.tiff *.tif *.webp *.gif"
        select_images = QFileDialog.getOpenFileNames(
            self, "Select Images", "", f"Images ({img_ext})"
        )

        self.file_tree.populate_tree(select_images[0], self)

    def add_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path == "":
            return

        self.file_tree.populate_tree([folder_path], self)

    def ascend_selected(self):
        if not self.file_tree.selectedIndexes():
            QMessageBox.warning(
                self, "Warning", "No items selected to ascend."
            )
            return

        self.file_tree.move_selected(-1)

    def descend_selected(self):
        if not self.file_tree.selectedIndexes():
            QMessageBox.warning(
                self, "Warning", "No items selected to descend."
            )
            return
        self.file_tree.move_selected(1)

    def sort_by_name(self):
        self.file_tree.sortItems(1, Qt.AscendingOrder)

    def remove_selected(self):
        if not self.file_tree.selectedIndexes():
            QMessageBox.warning(
                self, "Warning", "No items selected to remove."
            )
            return
        self.file_tree.remove_selected_rows()

    def select_save_directory(self):

        output_format = self.output_format_cb.currentText()
        output_path = self._get_output_path()
        if not output_path:
            return
        
        format = f"All Files (*.*)"
        if output_format in constants.OUTPUT_VIDEO_FORMAT:
            format = f"Video Files (*.{output_format})"
        elif output_format in constants.OUTPUT_IMAGE_FORMAT:
            format = f"Image Files (*.{output_format})"

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", f"{output_path}", format
        )

        self.save_path_le.setText(save_path)

    def _get_output_path(self):

        output_format = self.output_format_cb.currentText()
        checked_items = self.file_tree.get_checked_items()
        seq_paths, non_seq_paths = handler.parse_path_by_type(checked_items)

        if not seq_paths and not non_seq_paths:
            LOGGER.warning(
                "No items selected or when there is an none-sequence file in sequence folder."
            )
            QMessageBox.warning(
                self, "Warning", "No items selected or invalid sequence."
            )
            return None

        if output_format in constants.OUTPUT_VIDEO_FORMAT:
            if seq_paths and non_seq_paths or (seq_paths and not non_seq_paths):
                first_file_name = Path(seq_paths[0]).stem.split(".")[0]
                dir = Path(seq_paths[0]).parent
                output_path = str(dir / f"{first_file_name}.{output_format}")

            elif non_seq_paths:
                first_file_name = Path(non_seq_paths[0]).stem
                dir = Path(non_seq_paths[0]).parent
                output_path = str(dir / f"{first_file_name}.{output_format}")

        elif output_format in constants.OUTPUT_IMAGE_FORMAT:
            if seq_paths:
                padding_full_path = handler.get_padding_path(seq_paths, output_format)
                output_path = padding_full_path
            elif non_seq_paths:
                padding_full_path = handler.get_padding_path(
                    non_seq_paths, output_format, frame_padding=4
                )
                output_path = padding_full_path
        else:
            output_path = ""

        return output_path
    
    def convert_images(self):

        reply = QMessageBox.information(
            self, "Convert", "Do you want to convert the selected images?", 
            QMessageBox.Ok | QMessageBox.Cancel
        )
        if reply == QMessageBox.Cancel:
            return
        
        LOGGER.info("Starting conversion process.")

        valid = self.file_tree.validate_format()

        if not valid:
            return
        
        save_path = self.save_path_le.text()
        output_format = self.output_format_cb.currentText()
        checked_items = self.file_tree.get_checked_items()
        frame_rate = self.frame_rate_cb.currentText()
        codec = self.codec_cb.currentText()
        resize = self.resize_cb.currentText()


        LOGGER.info(f"Save Path: {save_path}")
        LOGGER.info(f"Format: {output_format}")
        LOGGER.info(f"Frame Rate: {frame_rate}")
        LOGGER.info(f"Codec: {codec}")
        LOGGER.info(f"Resize: {resize}")
        LOGGER.info(f"Checked Items: {checked_items}")


        converted = ffmpeg.run_conversion(
            save_path, output_format, checked_items, frame_rate=frame_rate, 
            codec=codec, resize=resize
        )

        if not converted:
            LOGGER.error("Conversion failed.")
            QMessageBox.critical(
                self, "Error", "Conversion failed."
            )

