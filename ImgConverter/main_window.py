import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(__file__))
from qt_compat import (
    Qt, QIcon, QFontDatabase, QFont, QWidget, QLabel, QPushButton, 
    QSizePolicy, QComboBox, QSpacerItem, QFrame, QHBoxLayout, QVBoxLayout,
    QGridLayout, QGroupBox, QApplication, QLineEdit, qdarktheme, QPixmap, 
)
from Widgets import push_button, tree_widget
import converter_constants as constants
from HANLib import init_logger

# Set Logger
log_name = "main_window"
log_dir = os.path.expanduser(r"~\Logs\ImgConverter")
log_path = str(Path(log_dir) / f"{log_name}.log")
LOGGER = init_logger.Logger(log_name, log_path)

RESOURCE_PATH = Path(constants.RESOURCE_PATH)

class ConverterUi(QWidget):
    def __init__(self, run_paths=None):
        super().__init__()

        self.clicked_file_path = ""
            
        self.__set_window()
        self.__set_font()
        self.__set_widgets()
        self.__set_layouts()
        self.__connect_signals()
        self.__change_event()
        qdarktheme.setup_theme()

        if run_paths:
            LOGGER.info(f"Running with paths: {run_paths}")
            self.file_tree.populate_tree(run_paths, self)

    def __set_window(self):
        if script_path.lower().startswith("u:"):
            self.setWindowTitle(f"Image Converter {constants.__VERSION__} [DEV]")
        else:
            self.setWindowTitle(f"Image Converter {constants.__VERSION__}")

        self.setWindowFlags(
            self.windowFlags() ^ Qt.WindowContextHelpButtonHint
        )
        self.setMinimumSize(1200, 700)
        self.setWindowIcon(QIcon(str(RESOURCE_PATH / "seq_to_mov.ico")))

    def __set_font(self):
        font_path = str(RESOURCE_PATH / "Lato-Bold.ttf")
        QFontDatabase.addApplicationFont(font_path)
        app_font = QFont("Lato")
        app_font.setPointSize(10)
        app_font.setStyleStrategy(QFont.PreferAntialias)
        QApplication.setFont(app_font)

    def __set_widgets(self):
        # Create menu buttons
        self.add_img_btn = push_button.MenuButton("file-circle-plus-solid.svg")
        self.add_img_layout = self.create_menu_button_layout(
            self.add_img_btn, " Add Images "
        )
        self.add_folder_btn = push_button.MenuButton("folder-plus-solid.svg")
        self.add_folder_layout = self.create_menu_button_layout(
            self.add_folder_btn, " Add Folder "
        )
        self.ascend_btn = push_button.MenuButton("arrow-up-solid.svg")
        self.ascend_layout = self.create_menu_button_layout(
            self.ascend_btn, " Ascend selected "
        )
        self.descend_btn = push_button.MenuButton("arrow-down-solid.svg")
        self.descend_layout = self.create_menu_button_layout(
            self.descend_btn, " Descend selected "
        )
        self.remove_btn = push_button.MenuButton("trash-solid.svg")
        self.remove_layout = self.create_menu_button_layout(
            self.remove_btn, " Remove selected "
        )
        self.name_sort_btn = push_button.MenuButton("sort-down-solid-full.svg")
        self.name_sort_layout = self.create_menu_button_layout(
            self.name_sort_btn, " Sort by name "
        )

        # Create input list tree widget
        self.file_tree = tree_widget.DragDropTreeWidget(self)

        # Create preview and file info widgets
        self.preview_lb = QLabel("Image Preview")
        self.preview_lb.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.preview_lb.setFont(QFont("Lato", 11))
        self.preview_img = QLabel()
        self.preview_img.setAlignment(Qt.AlignCenter)
        # self.preview_img.setMinimumSize(300, 200)

        # Create file info labels
        self.file_name_lb = self.create_label()
        self.file_format_lb = self.create_label()
        self.img_size_lb = self.create_label()
        self.file_size_lb = self.create_label()

        # Create conversion settings widgets
        self.convert_lb = QLabel("Conversion Settings")
        self.convert_lb.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.convert_lb.setFont(QFont("Lato", 11))

        # Slate options
        self.slate_btn = QPushButton("Add Slate")
        self.slate_btn.setFixedHeight(30)
        self.slate_btn.setFixedWidth(100)
        self.slate_btn.setFont(QFont("Lato", 10))

        # frame rate
        self.frame_rate_lb = self.create_label("Frame rate:")
        self.frame_rate_cb = QComboBox()
        self.frame_rate_cb.addItems(constants.FRAME_RATE)
        self.frame_rate_cb.setCurrentText("23.976")

        # codec
        self.codec_lb = self.create_label("Codec:")
        self.codec_cb = QComboBox()
        self.codec_cb.addItems(constants.CODEC)

        # resize
        self.resize_lb = self.create_label("Resize to:")
        self.resize_cb = QComboBox()
        self.resize_cb.addItems(constants.RESIZE)
        self.width_lb = self.create_label("Width:")
        self.width_le = QLineEdit()
        self.height_lb = self.create_label("Height:")
        self.height_le = QLineEdit()

        # format
        self.output_format_lb = self.create_label("Output format:")
        self.output_format_cb = QComboBox()
        self.output_format_cb.addItems(constants.OUTPUT_FORMAT)

        # save path
        self.save_path_lb = self.create_label("Save to:")
        self.save_path_le = QLineEdit()
        self.save_dir_btn = QPushButton("...")
        self.save_dir_btn.setFixedWidth(30)
        self.save_dir_btn.setFixedHeight(30)
        
        # Create convert button
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setFixedHeight(30)
        self.convert_btn.setFont(QFont("Lato", 11))

    def __change_event(self):
        self.output_format_cb.currentTextChanged.connect(self.set_conversion_settings)
        self.codec_cb.currentTextChanged.connect(self.set_output_format)
        self.resize_cb.currentTextChanged.connect(self.set_change_image_size)
        self.width_le.editingFinished.connect(self.get_custom_image_size)
        self.height_le.editingFinished.connect(self.get_custom_image_size)

    def set_conversion_settings(self):
        before_path = self.save_path_le.text() or ""
        self.save_path_le.clear()
        format = self.output_format_cb.currentText()
        widgets = [self.frame_rate_cb, self.codec_cb]

        if format in constants.OUTPUT_VIDEO_FORMAT:
            for widget in widgets:
                widget.setDisabled(False)

            codec = constants.EXT_WITH_CODEC.get(format, "")
            self.codec_cb.setCurrentText(codec)
            
        elif format in constants.OUTPUT_IMAGE_FORMAT:
            for widget in widgets:
                widget.setDisabled(True)
        
        self.set_save_path(before_path, format)

    def set_save_path(self, before_path, format):
        if not before_path:
            return
            
        stem = Path(before_path).stem
        before_format = Path(before_path).suffix.split(".")[-1]
        IMAGE = constants.OUTPUT_IMAGE_FORMAT
        VIDEO = constants.OUTPUT_VIDEO_FORMAT

        if before_format in IMAGE:
            if format in IMAGE:
                before_dir = Path(before_path).parent 
                save_path = str(before_dir / f"{stem}.{format}")
                self.save_path_le.setText(save_path)
            elif format in VIDEO:
                self.save_path_le.setText("")
        elif before_format in VIDEO:
            if format in VIDEO:
                before_dir = Path(before_path).parent
                save_path = str(before_dir / f"{stem}.{format}")
                self.save_path_le.setText(save_path)
            elif format in IMAGE:
                self.save_path_le.setText("")

    def set_output_format(self):
        self.save_path_le.clear()
        codec = self.codec_cb.currentText()
        ext = constants.CODEC_WITH_EXT.get(codec, "")
        self.output_format_cb.setCurrentText(ext)

    def set_change_image_size(self):
        resize = self.resize_cb.currentText()
        width = resize.split("(")[-1].split('x')[0]
        height = resize.split("(")[-1].split('x')[1].split(")")[0]
        self.width_le.setText(width)
        self.height_le.setText(height)

    def get_custom_image_size(self):
        width = self.width_le.text()
        height = self.height_le.text()

        if not width or not height:
            return None

        try:
            width = int(width)
            height = int(height)
        except ValueError:
            return None

        if width <= 0 or height <= 0:
            return None

        image_size = f"{width}x{height}"
        self.add_custom_image_size(image_size, "Custom")
    
    def add_custom_image_size(self, image_size=None, resize_type="Default"):

        if not self.resize_cb.findText(f"{resize_type}({image_size})")== -1:
            return
         
        if image_size:
            self.resize_cb.addItem(f"{resize_type}({image_size})")
            self.resize_cb.setCurrentText(f"{resize_type}({image_size})")
            self.width_le.setText(image_size.split('x')[0])
            self.height_le.setText(image_size.split('x')[1])

    def __connect_signals(self):
        self.file_tree.itemClicked.connect(self.update_preview)

    def update_preview(self, item):
        self.file_name_lb.clear()
        self.file_format_lb.clear()
        self.img_size_lb.clear()
        self.file_size_lb.clear()

        selected_items = self.file_tree.selectedItems()

        if not selected_items:
            return

        for selected_item in selected_items:
            if selected_item.parent(): # child
                item = selected_item
                file_name = item.text(self.file_tree.file_name_col)
            else: # parent
                parent = selected_item
                if parent.childCount() > 0:
                    file_name = parent.text(self.file_tree.file_name_col)
                else:
                    item = selected_item
                    file_name = item.text(self.file_tree.file_name_col)

        format = item.text(self.file_tree.format_col)
        img_size = item.text(self.file_tree.image_size_col)
        file_size = item.text(self.file_tree.file_size_col)
        self.clicked_file_path = item.text(self.file_tree.path_col)

        self.file_name_lb.setText(str(file_name))
        self.file_format_lb.setText(str(format).upper())
        self.img_size_lb.setText(str(img_size))
        self.file_size_lb.setText(str(file_size))

        pixmap = QPixmap(self.clicked_file_path)
        if pixmap.isNull():
            self.preview_img.setText("No preview available")
            return
        self.preview_img.setPixmap(pixmap.scaled(
            300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def create_menu_button_layout(self, button, button_text):

        button_label = QLabel(button_text)
        button_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        button_label.setFont(QFont("Lato", 10))

        button_layout = QVBoxLayout()
        button_layout.addWidget(button, 0, Qt.AlignCenter)
        button_layout.addWidget(button_label)
        button_layout.setAlignment(Qt.AlignCenter)

        return button_layout
    
    def create_line(self):
        liner = QFrame()
        liner.setFrameShape(QFrame.HLine)
        liner.setFrameShadow(QFrame.Sunken)

        return liner

    def create_spacer(self):
        return QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

    def create_label(self, text=""):
        label = QLabel(text)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setFont(QFont("Lato", 10))

        return label
        
    def __set_layouts(self):
        # left side layout
        # menu layout
        menu_layout = QHBoxLayout()
        menu_layout.addLayout(self.add_img_layout)
        menu_layout.addLayout(self.add_folder_layout)
        menu_layout.addLayout(self.ascend_layout)
        menu_layout.addLayout(self.descend_layout)
        menu_layout.addLayout(self.name_sort_layout)
        menu_layout.addLayout(self.remove_layout)
        menu_layout.addItem(self.create_spacer())

        left_layout = QGridLayout()
        left_layout.addLayout(menu_layout, 0, 0, 1, 3)
        left_layout.addWidget(self.file_tree, 2, 0, 1, 3)
        
        # right side layout
        # preview image layout
        prv_img_layout = QVBoxLayout()
        prv_img_layout.addWidget(self.preview_img)
        prv_img_grbx = QGroupBox()
        prv_img_grbx.setLayout(prv_img_layout)
        prv_img_grbx.setMinimumHeight(200)
        prv_img_grbx.setMinimumWidth(300)

        # file info layout
        file_info_layout = QVBoxLayout()
        file_info_layout.addWidget(self.file_name_lb)
        file_info_layout.addWidget(self.file_format_lb)
        file_info_layout.addWidget(self.img_size_lb)
        file_info_layout.addWidget(self.file_size_lb)

        # preview layout
        prv_layout = QVBoxLayout()
        prv_layout.addWidget(self.preview_lb)
        prv_layout.addWidget(self.create_line())
        prv_layout.addWidget(prv_img_grbx)
        prv_layout.addLayout(file_info_layout)
        prv_grbx = QGroupBox()
        prv_grbx.setLayout(prv_layout)

        # Resize to custom size layout
        resize_layout = QGridLayout()
        resize_layout.addWidget(self.resize_lb, 0, 0, 1, 2)
        resize_layout.addWidget(self.resize_cb, 0, 2, 1, 2)
        resize_layout.addWidget(self.width_lb, 1, 0)
        resize_layout.addWidget(self.width_le, 1, 1)
        resize_layout.addWidget(self.height_lb, 1, 2)
        resize_layout.addWidget(self.height_le, 1, 3)

        # conversion settings layout
        convert_settings_layout = QHBoxLayout()
        convert_settings_layout.addWidget(self.convert_lb, 0)
        convert_settings_layout.addStretch(1)
        convert_settings_layout.addWidget(self.slate_btn, 2)
        convert_layout = QGridLayout()
        convert_layout.addLayout(convert_settings_layout, 0, 0, 1, 2)
        convert_layout.addWidget(self.create_line(), 1, 0, 1, 2)
        convert_layout.addWidget(self.output_format_lb, 2, 0)
        convert_layout.addWidget(self.output_format_cb, 2, 1)
        convert_layout.addWidget(self.frame_rate_lb, 3, 0)
        convert_layout.addWidget(self.frame_rate_cb, 3, 1)
        convert_layout.addWidget(self.codec_lb, 4, 0)
        convert_layout.addWidget(self.codec_cb, 4, 1)
        convert_layout.addLayout(resize_layout, 5, 0, 1, 2)
        convert_grbx = QGroupBox()
        convert_grbx.setLayout(convert_layout)

        save_path_layout = QHBoxLayout()
        save_path_layout.addWidget(self.save_path_lb)
        save_path_layout.addWidget(self.save_path_le)
        save_path_layout.addWidget(self.save_dir_btn)

        right_layout = QVBoxLayout()
        right_layout.addWidget(prv_grbx)
        right_layout.addWidget(convert_grbx)
        right_layout.addSpacing(10) 
        right_layout.addLayout(save_path_layout)
        right_layout.addSpacing(10) 
        right_layout.addWidget(self.convert_btn)
        right_layout.addStretch()

        # Combine left and right layouts
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)
        
        self.setLayout(main_layout)

class SlateSettingsWindow(QWidget):
    def __init__(self, file_path=""):
        super().__init__()
        self.file_path = file_path
        self.__set_window()
        self.__set_widgets()
        self.__set_layouts()

    def __set_window(self):
        self.setWindowTitle("Slate Settings")
        self.setMinimumSize(1000, 600)
        self.setWindowFlags(
            self.windowFlags() ^ Qt.WindowContextHelpButtonHint
        )
        self.setWindowModality(Qt.ApplicationModal)

    def __set_widgets(self):
        # top options
        self.top_left_cb = QComboBox()
        self.top_left_cb.setMaximumWidth(200)
        self.top_center_cb = QComboBox()
        self.top_center_cb.setMaximumWidth(200)
        self.top_right_cb = QComboBox()
        self.top_right_cb.setMaximumWidth(200)
        self.top_left_lb = QLabel("top left")
        self.top_left_lb.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.top_center_lb = QLabel("top center")
        self.top_center_lb.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.top_right_lb = QLabel("top right")
        self.top_right_lb.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # bottom options
        self.bottom_left_cb = QComboBox()
        self.bottom_left_cb.setMaximumWidth(200)
        self.bottom_center_cb = QComboBox()
        self.bottom_center_cb.setMaximumWidth(200)
        self.bottom_right_cb = QComboBox()
        self.bottom_right_cb.setMaximumWidth(200)
        self.bottom_left_lb = QLabel("bottom left")
        self.bottom_left_lb.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.bottom_center_lb = QLabel("bottom center")
        self.bottom_center_lb.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.bottom_right_lb = QLabel("bottom right")
        self.bottom_right_lb.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # preview area
        self.preview_lb = QLabel()
        self._set_pixmap()

    def __set_layouts(self):
        # top layout
        top_cb_layout = QHBoxLayout()
        top_cb_layout.addWidget(self.top_left_cb)
        top_cb_layout.addWidget(self.top_center_cb)
        top_cb_layout.addWidget(self.top_right_cb)
        top_lb_layout = QHBoxLayout()
        top_lb_layout.addWidget(self.top_left_lb)
        top_lb_layout.addWidget(self.top_center_lb)
        top_lb_layout.addWidget(self.top_right_lb)

        # bottom layout
        bottom_cb_layout = QHBoxLayout()
        bottom_cb_layout.addWidget(self.bottom_left_cb)
        bottom_cb_layout.addWidget(self.bottom_center_cb)
        bottom_cb_layout.addWidget(self.bottom_right_cb)
        bottom_lb_layout = QHBoxLayout()
        bottom_lb_layout.addWidget(self.bottom_left_lb)
        bottom_lb_layout.addWidget(self.bottom_center_lb)
        bottom_lb_layout.addWidget(self.bottom_right_lb)

        # preview layout
        preview_layout = QVBoxLayout()
        preview_layout.addLayout(top_lb_layout)
        preview_layout.addWidget(self.preview_lb)
        preview_layout.addLayout(bottom_lb_layout)
        preview_layout.setAlignment(Qt.AlignCenter)
        preview_grbx = QGroupBox("Slate Preview")
        preview_grbx.setLayout(preview_layout)
        preview_grbx.setAlignment(Qt.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_cb_layout)
        main_layout.addWidget(preview_grbx)
        main_layout.addLayout(bottom_cb_layout)

        self.setLayout(main_layout)

    def _set_pixmap(self):
        if self.file_path:
            pixmap = QPixmap(self.file_path)
            if pixmap.isNull():
                self.preview_pixmap = QPixmap(900, 450)
                self.preview_pixmap.fill(Qt.darkGray)
                self.preview_lb.setPixmap(self.preview_pixmap)
                return
            self.preview_lb.setPixmap(pixmap.scaled(
                900, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        else:
            self.preview_pixmap = QPixmap(900, 450)
            self.preview_pixmap.fill(Qt.darkGray)
            self.preview_lb.setPixmap(self.preview_pixmap)
