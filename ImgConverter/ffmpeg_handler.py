import os
import sys
import subprocess
from pathlib import Path

from qt_compat import QMessageBox
import file_handler as handler
import converter_constants as constants
from HANLib import init_logger

# Set Logger
log_name = "ffmpeg_handler"
log_dir = os.path.expanduser(r"~\Logs\ImgConverter")
log_path = str(Path(log_dir) / f"{log_name}.log")
LOGGER = init_logger.Logger(log_name, log_path)

def run_conversion(
        save_path, output_format, checked_items, frame_rate=None, 
        codec=None, resize=None
):
    cmd = ""
    txt_file_path = save_path.replace(f".{output_format}", ".txt")
    seq_paths, non_seq_paths = handler.parse_path_by_type(checked_items)
    resize_cmd = get_resize_cmd(resize)

    if output_format in constants.OUTPUT_VIDEO_FORMAT:

        if frame_rate == "23.976":
            frame_rate = "24000/1001"

        for codec_data in constants.FFMPEG_CMD_DATA:
            if codec == codec_data.get("name"):
                codec_cmd = codec_data.get("codec")
                break

        if seq_paths and non_seq_paths:
            paths = seq_paths + non_seq_paths
            cmd = set_none_seq_to_video_cmd(
                paths, save_path, frame_rate, txt_file_path, codec_cmd, resize_cmd
            )
        elif seq_paths and not non_seq_paths:
            cmd = set_seq_to_video_cmd(
                seq_paths, save_path, frame_rate, codec_cmd, resize_cmd
            )
        elif not seq_paths and non_seq_paths:
            cmd = set_none_seq_to_video_cmd(
                non_seq_paths, save_path, frame_rate, txt_file_path, codec_cmd, resize_cmd
            )

    elif output_format in constants.OUTPUT_IMAGE_FORMAT:
        if seq_paths and non_seq_paths:
            paths = seq_paths + non_seq_paths
            if output_format == "exr":
                cmd = set_none_seq_to_exr_cmd(paths, save_path, txt_file_path, resize_cmd)
            else:
                cmd = set_none_seq_to_img_cmd(paths, save_path, txt_file_path, resize_cmd)
        elif seq_paths and not non_seq_paths:
            if output_format == "exr":
                cmd = set_seq_to_exr_cmd(seq_paths, save_path, resize_cmd)
            else:
                cmd = set_seq_to_img_cmd(seq_paths, save_path, resize_cmd)
        elif not seq_paths and non_seq_paths:
            if output_format == "exr":
                cmd = set_none_seq_to_exr_cmd(non_seq_paths, save_path, txt_file_path, resize_cmd)
            else:
                cmd = set_none_seq_to_img_cmd(non_seq_paths, save_path, txt_file_path, resize_cmd)


    if not cmd:
        LOGGER.error("Failed to create ffmpeg command.")
        QMessageBox.critical(
            None, "Error", "Failed to create ffmpeg command."
        )
        return False

    LOGGER.info(f"Executing command: {cmd}")
    execute_cmd(cmd, os.path.dirname(save_path))

    if os.path.exists(txt_file_path):
        os.remove(txt_file_path)

    return True

def set_none_seq_to_video_cmd(
        paths, save_path, frame_rate, txt_file_path, codec_cmd, resize_cmd
    ):

    made = make_image_list(paths, txt_file_path)
    if not made:
        return None

    cmd = (
        f'ffmpeg '
        f'-y '
        f'-f concat -safe 0 '
        f'-i "{txt_file_path}" '
        f'-c:v {codec_cmd} {resize_cmd} '
        f'-r {frame_rate} '
        f'{save_path}'
    )
    
    return cmd

def set_seq_to_video_cmd(
        seq_paths, save_path, frame_rate, codec_cmd, resize_cmd
    ):

    frames = handler.get_frames(seq_paths)
    valid = _validate_frame_number(frames)
    if not valid:
        return None
    
    input_ext = Path(seq_paths[0]).suffix.lstrip(".")
    input_padding_path = handler.get_padding_path(seq_paths, input_ext)
    start_frame = sorted(frames)[0]

    cmd = (
        f'ffmpeg '
        f'-y '
        f'-start_number {start_frame} '
        f'-framerate {frame_rate} '
        f'-i "{input_padding_path}" '
        f'-vframes {len(frames)} '
        f'-c:v {codec_cmd} {resize_cmd} '
        f'-r {frame_rate} '
        f'{save_path}'
    )

    return cmd

def set_seq_to_exr_cmd(seq_paths, save_path, resize_cmd):

    frames = handler.get_frames(seq_paths)
    valid = _validate_frame_number(frames)
    if not valid:
        return None

    start_frame = sorted(frames)[0]
    input_ext = Path(seq_paths[0]).suffix.lstrip(".")
    input_padding_path = handler.get_padding_path(seq_paths, input_ext)

    cmd = (
        f'ffmpeg '
        f'-y '
        f'-start_number {start_frame} '
        f'-i "{input_padding_path}" '
        f'{resize_cmd} '
        f'-vframes {len(frames)} '
        f'-c:v exr -pix_fmt rgb48 '
        f'{save_path}'
    )
    return cmd

def set_none_seq_to_exr_cmd(paths, save_path, txt_file_path, resize_cmd):

    import re
    pattern =  r"%\d*d\.?"
    if re.search(pattern, txt_file_path):
        txt_file_path = re.sub(pattern, "", txt_file_path)

    made = make_image_list(paths, txt_file_path)
    if not made:
        return None
    
    cmd = (
        f'ffmpeg '
        f'-y '
        f'-f concat -safe 0 '
        f'-i "{txt_file_path}" '
        f'{resize_cmd} '
        f'-c:v exr -pix_fmt rgb48 '
        f'{save_path}'
    )
    return cmd

def set_seq_to_img_cmd(seq_paths, save_path, resize_cmd):

    frames = handler.get_frames(seq_paths)
    valid = _validate_frame_number(frames)
    if not valid:
        return None

    start_frame = sorted(frames)[0]
    input_ext = Path(seq_paths[0]).suffix.lstrip(".")
    input_padding_path = handler.get_padding_path(seq_paths, input_ext)

    cmd = (
        f'ffmpeg '
        f'-y '
        f'-start_number {start_frame} '
        f'-i "{input_padding_path}" '
        f'{resize_cmd} '
        f'-vframes {len(frames)} '
        f'-q:v 2 '
        f'{save_path}'
    )
    return cmd

def set_none_seq_to_img_cmd(paths, save_path, txt_file_path, resize_cmd):

    made = make_image_list(paths, txt_file_path)
    if not made:
        return None

    cmd = (
        f'ffmpeg '
        f'-y '
        f'-f concat -safe 0 '
        f'-i "{txt_file_path}" '
        f'{resize_cmd} '
        f'-q:v 2 '
        f'{save_path}'
    )
    return cmd

def get_resize_cmd(resize):
    
    width = resize.split("(")[-1].split('x')[0]
    height = resize.split("(")[-1].split('x')[1].split(")")[0]

    resize_cmd = (
        f"-vf "
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black"
    )

    return resize_cmd

def execute_cmd(cmd, save_dir):
    try:
        process = subprocess.Popen(cmd, shell=True)
        process.wait()
        
        if process.returncode == 0:
            LOGGER.info("Conversion completed successfully.")
            QMessageBox.information(
                None, "Information", "Conversion is done"
            )
            os_name = sys.platform
            if os_name == "win32":
                os.startfile(save_dir)
            elif os_name == "darwin":
                subprocess.run(["open", save_dir])
        else:
            LOGGER.error(f"Conversion failed. {cmd}")
            QMessageBox.critical(
                None, "Error", f"Conversion failed \n\nCommand: {cmd}"
            )
    except Exception as e:
        LOGGER.error(f"Conversion failed: {e} \n\nCommand: {cmd}")
        QMessageBox.critical(
            None, "Error", f"Conversion failed: {e} \n\nCommand: {cmd}"
        )

def make_image_list(paths: list[str], text_path: str):

    with open(text_path, 'w', encoding='utf-8') as f:
        for path in paths:
            f.write(f"file '{path}'\n")

    if not os.path.exists(text_path):
        return False

    return True

def _validate_frame_number(frames: list[str]) -> bool:

    if not frames:
        return False

    frames = sorted([int(f) for f in frames])
    if frames != list(range(min(frames), max(frames) + 1)):
        LOGGER.warning(
            "The selected sequence has missing frames."
        )
        QMessageBox.warning(
            None, "Warning", 
            "The selected sequence has missing frames. Please select a complete sequence."
        )
        return False
    return True


