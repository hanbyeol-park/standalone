try:

    from PySide6.QtCore import ( 
        Qt, QSize, QItemSelectionModel, Signal, QTimer, QRect
    )
    from PySide6.QtGui import QIcon, QFontDatabase, QFont, QPixmap, QPainter
    from PySide6.QtWidgets import (
        QWidget, QLabel, QPushButton, QSizePolicy, QComboBox, QSpacerItem, 
        QFrame, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, 
        QApplication, QCheckBox, QTableWidget, QLineEdit, QSpinBox, 
        QAbstractItemView, QTableWidgetItem, QFileDialog, QMessageBox, 
        QHeaderView, QDoubleSpinBox, QStyleOptionButton, QStyle, QTreeWidget,
        QTreeWidgetItem
    )
    
except ImportError:
    from PySide2.QtCore import (
        Qt, QSize, QItemSelectionModel, Signal, QTimer, QRect
    )
    from PySide2.QtGui import QIcon, QFontDatabase, QFont, QPixmap, QPainter
    from PySide2.QtWidgets import (
        QWidget, QLabel, QPushButton, QSizePolicy, QComboBox, QSpacerItem, 
        QFrame, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, 
        QApplication, QCheckBox, QTableWidget, QLineEdit, QSpinBox, 
        QAbstractItemView, QTableWidgetItem, QFileDialog, QMessageBox, 
        QHeaderView, QDoubleSpinBox, QStyleOptionButton, QStyle, QTreeWidget,
        QTreeWidgetItem
    )

import qdarktheme