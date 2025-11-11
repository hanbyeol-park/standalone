import os
import sys
import re
from pathlib import Path

from HANLib import storage_paths
STORAGE = storage_paths.StoragePaths()

__VERSION__ = "2.0"

os_name = sys.platform

if os_name == "win32":
    root_path = STORAGE.CORE
    ffmpeg_path = r"C:\site-packages\ffmpeg\7.1"

elif os_name == "darwin":
    root_path = STORAGE.get("CORE", system="Darwin")
    root_path = STORAGE
    ffmpeg_dir = Path("/your/file/path/ffmpeg")
    ver_list = []
    for dir in ffmpeg_dir.iterdir():
        if dir.is_file():
            continue
        if re.match(r"^\d+\.\d+\.(\d+|\d+_\d+)$", dir.name):
            dir = str(dir)
            ver_list.append(dir)
    ffmpeg_path = sorted(ver_list)[-1]

os.environ["PATH"] += os.pathsep + ffmpeg_path

file_dir = Path(__file__).parent
RESOURCE_PATH = str(file_dir / "Resources")

TABLE_HEADER = ["", "File Name", "Format", "Image Size", "File Size", "Path"]

INPUT_IMAGE_FORMAT = [
    ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".exr", "tiff", ".tif", ".webp"
]

FRAME_RATE = [
    "23.976", "24", "25", "29.97", "30", "59.94", "60", "120", "240"
]

CODEC = [
    "ProRes 4:4:4:4 XQ 12-bit", "ProRes 4:4:4:4 12-bit", 
    "ProRes 4:2:2 HQ 10-bit", "ProRes 4:2:2 10-bit",
    "ProRes 4:2:2 LT 10-bit", "ProRes 4:2:2 Proxy 10-bit",
    "H.264", "MPEG-4", "DNxHD 422 8-bit 36Mbit", ""
    ]

RESIZE = [
    "FHD(1920x1080)", "HD(1280x720)", "2K(2048x1080)", "QHD(2560x1440)", 
    "UHD(3840x2160)", "4K(3840x2160)"
]

OUTPUT_VIDEO_FORMAT = ["mov", "mp4", "avi"]
OUTPUT_IMAGE_FORMAT = ["jpg", "png", "exr"]
OUTPUT_FORMAT = OUTPUT_VIDEO_FORMAT + OUTPUT_IMAGE_FORMAT

FFMPEG_CMD_DATA = [{
    "name": "H.264",
    "codec": "libx264 -crf 15 -preset slow",
},
{
    "name": "MPEG-4",
    "codec": "mpeg4 -q:v 2",
},
{
    "name": "ProRes 4:2:2 HQ 10-bit",
    "codec": "prores_ks -profile:v 3 -pix_fmt yuv422p10le",
},
{
    "name": "ProRes 4:4:4:4 XQ 12-bit",
    "codec": "prores_ks -profile:v 5 -pix_fmt yuva444p12le",
},
{
    "name": "ProRes 4:4:4:4 12-bit",
    "codec": "prores_ks -profile:v 4 -pix_fmt yuva444p12le",
},
{
    "name": "ProRes 4:2:2 10-bit",
    "codec": "prores_ks -profile:v 2 -pix_fmt yuv422p10le",
},
{
    "name": "ProRes 4:2:2 LT 10-bit",
    "codec": "prores_ks -profile:v 1 -pix_fmt yuv422p10le",
},
{
    "name": "ProRes 4:2:2 Proxy 10-bit",
    "codec": "prores_ks -profile:v 0 -pix_fmt yuv422p10le",
},
{
    "name": "DNxHD 422 8-bit 36Mbit",
    "codec": "dnxhd -b:v 36M -pix_fmt yuv422p"
}
]

CODEC_WITH_EXT = {
    "H.264": "mp4",
    "MPEG-4": "avi",
    "ProRes 4:4:4:4 XQ 12-bit": "mov",
    "ProRes 4:4:4:4 12-bit": "mov",
    "ProRes 4:2:2 HQ 10-bit": "mov",
    "ProRes 4:2:2 10-bit": "mov",
    "ProRes 4:2:2 LT 10-bit": "mov",
    "ProRes 4:2:2 Proxy 10-bit": "mov",
    "DNxHD 422 8-bit 36Mbit": "mov"
}

EXT_WITH_CODEC = {
    "mp4": "H.264",
    "mov": "ProRes 4:4:4:4 XQ 12-bit",
    "avi": "MPEG-4",
    "jpg": "",
    "png": "",
    "exr": ""
}

if __name__ == "__main__":
    print(RESOURCE_PATH)