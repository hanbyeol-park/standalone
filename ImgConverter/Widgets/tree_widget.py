import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.dirname(__file__))

from qt_compat import (
    QTreeWidget, QApplication, Qt, QTreeWidgetItem, QAbstractItemView, QMessageBox
)
import converter_constants as constants
import file_handler as handler
from HANLib import init_logger

# Set Logger
log_name = "tree_widget"
log_dir = os.path.expanduser(r"~\Logs\ImgConverter")
log_path = str(Path(log_dir) / f"{log_name}.log")
LOGGER = init_logger.Logger(log_name, log_path)

class DragDropTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(DragDropTreeWidget, self).__init__(parent)
        self.window_ui = None
        self.constants_column()
        self.set_tree_widget()
        self.setup_drag_drop()
        self.toggle_all_checkboxes(True)
        self.itemChanged.connect(self.sync_children_with_parent)

    def constants_column(self):
        self.checkbox_col = 0
        self.file_name_col = 1
        self.format_col = 2
        self.image_size_col = 3
        self.file_size_col = 4
        self.path_col = 5

    def setup_drag_drop(self):
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): # outside
            event.acceptProposedAction()
        elif event.source() == self: # inside
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls(): # outside
            event.acceptProposedAction()
        elif event.source() == self: # inside
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls(): # outside
            paths = []
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isfile(path) or os.path.isdir(path):
                    paths.append(path)

            if not paths:
                return
            
            self.populate_tree(paths, self.window_ui)
            event.acceptProposedAction()

        elif event.source() == self: # inside
            super().dropEvent(event)
        else:
            event.ignore()

    def set_tree_widget(self):
        self.setMinimumWidth(800)

        headers = constants.TABLE_HEADER
        self.setColumnCount(len(headers))
        self.setHeaderLabels(headers)

        self.setColumnWidth(self.checkbox_col, 65)
        self.setColumnWidth(self.file_name_col, 200)
        self.setColumnWidth(self.format_col, 80)
        self.setColumnWidth(self.image_size_col, 100)
        self.setColumnWidth(self.file_size_col, 100)
        self.setColumnWidth(self.path_col, 300)

        self.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.setSelectionBehavior(QTreeWidget.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)

    def populate_tree(self, paths: list[str], window_ui=None):

        seq_info, non_seq_info = handler.get_paths_info(paths)

        if not seq_info and not non_seq_info:
            return

        if seq_info:
            for dir_name, file_info in seq_info['sequence'].items():
                tree_item = QTreeWidgetItem(self)
                tree_item.setFlags(tree_item.flags() | Qt.ItemIsUserCheckable)
                tree_item.setCheckState(self.checkbox_col, Qt.Checked)
                tree_item.setText(self.format_col, file_info[0].get("format", ""))
                tree_item.setText(self.image_size_col, file_info[0].get("image_size", ""))
                seq_path = str(Path(file_info[0].get("path", "")).parent)
                tree_item.setText(self.path_col, seq_path)
                frame_count = len(file_info)
                dir_info = f"{dir_name} ({frame_count})"
                tree_item.setText(self.file_name_col, dir_info)

                child_items = [QTreeWidgetItem(tree_item) for _ in range(len(file_info))]
                for i, info in enumerate(file_info):

                    result = self.validate_path([info["path"]])
                    if result is False:
                        index = self.indexOfTopLevelItem(tree_item)
                        self.takeTopLevelItem(index)
                        return

                    child_items[i].setFlags(child_items[i].flags() | Qt.ItemIsUserCheckable)
                    child_items[i].setCheckState(self.checkbox_col, Qt.Checked)
                    child_items[i].setText(self.file_name_col, info["file_name"])
                    child_items[i].setText(self.format_col, info["format"])
                    child_items[i].setText(self.image_size_col, info["image_size"])
                    child_items[i].setText(self.file_size_col, info["file_size"])
                    child_items[i].setText(self.path_col, info["path"])

                tree_item.addChildren(child_items)
                self.addTopLevelItem(tree_item)
                self.add_new_resize_option(file_info, dir_name, window_ui)

        if non_seq_info:
            for none_seq in non_seq_info['none_sequence']:
                result = self.validate_path([none_seq["path"]])
                if result is False:
                    return
                tree_item = QTreeWidgetItem(self)
                tree_item.setFlags(tree_item.flags() | Qt.ItemIsUserCheckable)
                tree_item.setCheckState(self.checkbox_col, Qt.Checked)
                tree_item.setText(self.file_name_col, none_seq["file_name"])
                tree_item.setText(self.format_col, none_seq["format"])
                tree_item.setText(self.image_size_col, none_seq["image_size"])
                tree_item.setText(self.file_size_col, none_seq["file_size"])
                tree_item.setText(self.path_col, none_seq["path"])
                self.addTopLevelItem(tree_item)

    def add_new_resize_option(self, file_info: dict, dir_name: str, window_ui=None):
        if not window_ui:
            return

        self.window_ui = window_ui
        img_size = file_info[0].get("image_size", "").replace(" ", "")
        new_size = f"{dir_name}({img_size})"
        cannot_find = -1
        if self.window_ui.resize_cb.findText(new_size) == cannot_find:
            self.window_ui.resize_cb.insertSeparator(len(constants.RESIZE))
            self.window_ui.resize_cb.addItem(new_size)

    def remove_selected_rows(self):
        selected_items = self.selectedItems()

        for item in selected_items:
            parent = item.parent()
            if parent:
                index = parent.indexOfChild(item)
                parent.takeChild(index)
            else:
                index = self.indexOfTopLevelItem(item)
                self.takeTopLevelItem(index)

    def move_selected(self, direction):
        self.setSortingEnabled(False)
        items = self.selectedItems()
        if not items:
            return
        
        parent = items[0].parent()
        if parent:
            all_children = [parent.child(i) for i in range(parent.childCount())]
        else:
            all_children = [self.topLevelItem(i) for i in range(self.topLevelItemCount())]

        indices = [all_children.index(i) for i in items]

        if direction < 0: # up
            indices.sort()
        else: # down
            indices.sort(reverse=True)

        for idx in indices:
            item = all_children[idx]
            if parent:
                parent.takeChild(idx)
                new_index = idx + direction
                new_index = max(0, min(new_index, parent.childCount()))
                parent.insertChild(new_index, item)                
            else:
                self.takeTopLevelItem(idx)
                new_index = idx + direction
                new_index = max(0, min(new_index, self.topLevelItemCount()))
                self.insertTopLevelItem(new_index, item)                

        for item in items:
            item.setSelected(True)

    def validate_path(self, paths: list[str]):

        if not paths:
            return True
        
        if self.topLevelItemCount() == 0:
            return True

        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i) # parents
            if item.childCount() > 0: # children 
                for j in range(item.childCount()):
                    child = item.child(j)
                    tree_path = child.text(self.path_col)
                    if tree_path in paths:
                        return False

            tree_path = item.text(self.path_col)
            if tree_path in paths:
                return False

        return True

    def get_checked_items(self) -> dict:
        checked_paths = {}
        for i in range(self.topLevelItemCount()):
            parent = self.topLevelItem(i)
            index = self.indexOfTopLevelItem(parent)

            if parent.childCount() == 0: 
                if parent.checkState(self.checkbox_col) != Qt.Checked:
                    continue
                checked_paths[index] = {"type": "non_seq", "path": {0: parent.text(self.path_col)}}

            elif parent.childCount() > 0:
                for j in range(parent.childCount()):
                    child = parent.child(j)
                    if parent.checkState(self.checkbox_col) != Qt.Checked:
                        if child.checkState(self.checkbox_col) != Qt.Checked:
                            continue
                        child_path = child.text(self.path_col)
                        checked_paths[f"{index}-{j}"] = {"type": "non_seq", "path": {0: child_path}}
                    elif parent.checkState(self.checkbox_col) == Qt.Checked:
                        if index not in checked_paths:
                            checked_paths[index] = {"type": "seq", "path": {}}

                        child_index = parent.indexOfChild(child)
                        seq_child_index = f"{index}-{child_index}"
                        checked_paths[index]["path"][seq_child_index] = child.text(self.path_col)
            

        LOGGER.info(f"Count of Checked Items: {len(checked_paths)}")
        return checked_paths

    def toggle_all_checkboxes(self, checked: bool):
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if not item.flags() & Qt.ItemIsUserCheckable:
                continue
            item.setCheckState(self.checkbox_col, Qt.Checked if checked else Qt.Unchecked)
            for j in range(item.childCount()):
                child = item.child(j)
                if not child.flags() & Qt.ItemIsUserCheckable:
                    continue
                child.setCheckState(
                    self.checkbox_col,
                    Qt.Checked if checked else Qt.Unchecked
                )

    def sync_children_with_parent(self, item: QTreeWidgetItem):

        if item.parent(): # child
            parent = item.parent()
            child = item
            if not child.flags() & Qt.ItemIsUserCheckable:
                return
            if child.checkState(self.checkbox_col) != Qt.Checked:
                self.blockSignals(True)
                parent.setCheckState(self.checkbox_col, Qt.Unchecked)
                self.blockSignals(False)
                return
            
            else:
                for j in range(parent.childCount()):
                    sibling = parent.child(j)
                    if not sibling.flags() & Qt.ItemIsUserCheckable:
                        continue
                    if sibling != child:
                        if sibling.checkState(self.checkbox_col) == Qt.Checked:
                            checked_count = sum(
                                1 for k in range(parent.childCount())
                                if parent.child(k).checkState(self.checkbox_col) == Qt.Checked
                            )
                            if checked_count == parent.childCount():
                                parent.setCheckState(self.checkbox_col, Qt.Checked)
                            return
                            
        elif item.parent() is None: # parent
            parent = item
            if not parent.flags() & Qt.ItemIsUserCheckable:
                return
            for j in range(parent.childCount()):
                child = parent.child(j)
                if not child.flags() & Qt.ItemIsUserCheckable:
                    continue
                child.setCheckState(
                    self.checkbox_col, 
                    parent.checkState(self.checkbox_col)
                    )

    def validate_format(self):

        if self.topLevelItemCount() == 0:
            return False

        formats = set()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i) 
            if item.checkState(self.checkbox_col) != Qt.Checked:
                continue
            if item.childCount() > 0: 
                for j in range(item.childCount()):
                    child = item.child(j)
                    if child.checkState(self.checkbox_col) != Qt.Checked:
                        continue
                    format = child.text(self.format_col)
                    formats.add(format)
            elif item.childCount() == 0:
                formats.add(item.text(self.format_col))

        formats = tuple(formats)

        if len(formats) > 1:
            LOGGER.warning(
                f"Multiple file formats selected: {formats}."
            )
            QMessageBox.warning(
                self, "Warning", 
                f"Multiple file formats selected:\n "
                f"{formats}\n "
                f"Please select files with the same format."
            )
            return False
        return True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DragDropTreeWidget()
    window.show()
    window.populate_tree([r'C:\Users\PHB\Pictures'])
    sys.exit(app.exec())