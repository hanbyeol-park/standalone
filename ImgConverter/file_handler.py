import os
import re
from pathlib import Path

import OpenImageIO as oiio

import converter_constants as constants

from HANLib import init_logger

# Set Logger
log_name = "file_handler"
log_dir = os.path.expanduser(r"~\Logs\ImgConverter")
log_path = str(Path(log_dir) / f"{log_name}.log")
LOGGER = init_logger.Logger(log_name, log_path)

def get_paths_info(paths: list[str]):

    if not paths:
        return None, None

    full_paths, dirs = _validate_path_or_dir(paths)

    seq_info, none_seq_info = None, None
    if full_paths:
        valid_images = _validate_image(full_paths)
        if valid_images:
            sequence, none_seq = _validate_sequence(valid_images)

            if sequence:
                seq_info = get_file_info(sequence, "sequence")
            if none_seq:
                none_seq_info = get_file_info(none_seq, "none_sequence")
    
    if dirs:
        for dir in dirs:
            dir = Path(dir)
            paths_in_dir = [str(path_in_dir) for path_in_dir in dir.iterdir()]

            child_seq, child_none_seq = get_paths_info(paths_in_dir)

            if child_seq:
                if seq_info is None:
                    seq_info = child_seq
                else:
                    for k, v in child_seq['sequence'].items():
                        if k in seq_info['sequence']:
                            seq_info['sequence'][k].extend(v) 
                        else:
                            seq_info['sequence'][k] = v

            if child_none_seq:
                none_seq_info = (
                    child_none_seq if not none_seq_info
                    else {"none_sequence": none_seq_info["none_sequence"] + child_none_seq["none_sequence"]}
                )

    return seq_info, none_seq_info

def _validate_path_or_dir(paths: list[str]):

    full_paths = []
    dirs = []
    for path in paths:
        if Path(path).is_file():
            full_paths.append(str(path))
        elif Path(path).is_dir():
            dirs.append(str(path))
    return full_paths, dirs

def _validate_image(path: list):

    if not path:
        return None
    
    valid_images = []
    for img in path:
        if Path(img).suffix.lower() in constants.INPUT_IMAGE_FORMAT:
            valid_images.append(img)

    return valid_images if valid_images else None

def _validate_sequence(paths: list[str]):

    if not paths:
        return None, None
    
    pattern = r"\.(\d+)\."

    sequence = []
    none_seq = []
    for path in paths:
        match = re.search(pattern, path)

        if match:
            sequence.append(path) 
        else:
            none_seq.append(path)

    return sequence if sequence else None, none_seq if none_seq else None

def get_file_info(paths: list[str], file_type: str):
    
    if not paths:
        return None

    file_info = {file_type: []}

    if file_type == "sequence":
        shot_dict = {}
        for path in paths:
            dir_name = Path(path).parent.name
            file_name = Path(path).name
            image_size = _get_image_size(str(path))
            if not image_size:
                image_size = "N/A"
            file_size = _get_file_size(str(path))
            if not file_size:
                file_size = "N/A"
            format = Path(path).suffix.split(".")[-1]

            if dir_name not in shot_dict:
                shot_dict[dir_name] = []

            shot_dict[dir_name].append({
                "file_name": file_name,
                "format": format,
                "image_size": image_size,
                "file_size": file_size,
                "path": str(path),
            })

        file_info[file_type] = shot_dict

    elif file_type == "none_sequence":
        for image in paths:
            image_path = Path(image)
            file_name = str(image_path.name)
            image_size = _get_image_size(str(image_path))
            if not image_size:
                image_size = "N/A"
            file_size = _get_file_size(str(image_path))
            if not file_size:
                file_size = "N/A"
            format = Path(image).suffix.split(".")[-1]

            file_dic = {
                "file_name": file_name,
                "format": format,
                "image_size": image_size,
                "file_size": file_size,
                "path": str(image_path),
            }

            file_info[file_type].append(file_dic)

    return file_info

def _get_image_size(path: str):

    if Path(path).suffix.lower() not in constants.INPUT_IMAGE_FORMAT:
        return None

    img = oiio.ImageInput.open(str(path))
    spec = img.spec()
    img_size = f"{spec.width} x {spec.height}"
    img.close()
    return img_size if img_size else None

def _get_file_size(path: str):

    if Path(path).suffix.lower() not in constants.INPUT_IMAGE_FORMAT:
        return None

    file_size = os.path.getsize(path)

    if file_size < 1024:
        return f"{file_size} B"
    elif file_size < 1024 ** 2:
        return f"{file_size / 1024:.2f} KB"
    elif file_size < 1024 ** 3:
        return f"{file_size / 1024 ** 2:.2f} MB"
    else:
        return f"{file_size / 1024 ** 3:.2f} GB"

def parse_path_by_type(checked_items: dict):

    seq_list = []
    non_seq_list = []

    for entry in checked_items.values():
        if entry["type"] == "seq":
            seq_list.extend(entry["path"].values())
        else:
            non_seq_list.extend(entry["path"].values())

    return seq_list, non_seq_list

def get_padding_path(paths: list[str], ext: str, frame_padding=None) -> str | None:

    if not frame_padding:
        frame_padding = _get_frame_padding(paths)

    frame_padding_cmd = f"%0{frame_padding}d"
    path = paths[0]
    dir = Path(path).parent
    shot_name = Path(path).stem.split(".")[0]
    padding_file_name = f"{shot_name}.{frame_padding_cmd}.{ext}"
    padding_full_path = str(Path(dir) / padding_file_name)

    return padding_full_path

def _get_frame_padding(paths: list[str]) -> str | None: 

    frames = get_frames(paths)

    frame_padding = len(str(max(frames))) if frames else 0

    if frame_padding < 1:
        return None

    return frame_padding

def get_frames(paths: list[str]) -> list[str]:
    if not paths:
        return None
    
    pattern = r"\.(\d+)\."
    
    frames = []
    for path in paths:
        match = re.search(pattern, path)
        if not match:
            continue
        frame_number = match.group(1) if match.group(1).isdigit() else ""
        frames.append(frame_number)

    return frames
