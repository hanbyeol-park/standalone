import os
import sys

sys.path.append(os.path.dirname(__file__))

from qt_compat import QApplication
from Widgets import push_button

def parse_file_args(raw_args):
    combined = raw_args[0]
    return combined.split()

def main():
    app = QApplication(sys.argv)

    raw_args = sys.argv[1:]

    file_paths = parse_file_args(raw_args) if raw_args else []

    window = push_button.ButtonEventHandler(file_paths)
    window.show()

    sys.exit(app.exec())
    

if __name__ == "__main__":
    main()
