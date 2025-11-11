import os
import sys
from pathlib import Path
    
from HANLib import init_logger

sys.path.append(os.path.dirname(__file__))
from main_window import SlateSettingsWindow
import file_handler as handler

# Set Logger
log_name = "slate_handler"
log_dir = os.path.expanduser(r"~\Logs\ImgConverter")
log_path = str(Path(log_dir) / f"{log_name}.log")
LOGGER = init_logger.Logger(log_name, log_path)


class SlateHandler():
    def __init__(self, file_path="", checked_items=None):
        self.file_path = file_path
        self.checked_items = checked_items

        self.get_data()
        self.open_slate_window()

    def open_slate_window(self):
        self.slate_window = SlateSettingsWindow(self.file_path)
        self.slate_window.show()

    def get_data(self):
        start_frame, end_frame, frame_range = self.get_frame_data()

    def get_frame_data(self):
        seq_paths, non_seq_paths = handler.parse_path_by_type(self.checked_items)
        frames = handler.get_frames(seq_paths)

        start_frame = int(min(frames)) if frames else None
        end_frame = int(max(frames)) if frames else None
        duration = (end_frame - start_frame + 1) if frames else None
        frame_range = f"{start_frame}-{end_frame} ({duration})" if frames else "N/A"

        return start_frame, end_frame, frame_range