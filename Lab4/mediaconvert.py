import sys
import subprocess
from datetime import datetime
from utils import *

def mediaconvert():
    if len(sys.argv) < 3:
        return

    input_dir = sys.argv[1]
    target_format = sys.argv[2]

    output_dir = get_output_dir()
    history_file = os.path.join(output_dir, "history.csv")

    files = find_media_files(input_dir)
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')

    for file_path in files:
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d%H%M%S")
        date_time_str = now.strftime("%d-%m-%Y %H:%M:%S")

        name = os.path.basename(file_path)
        name_without_ext, _ = os.path.splitext(name)

        new_filename = f"{timestamp_str}-{name_without_ext}.{target_format}"
        output_path = os.path.join(output_dir, new_filename)

        is_image = file_path.lower().endswith(image_extensions)
        if is_image:
            program = "magick"
            subprocess.run(
                [program, file_path, output_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            program = "ffmpeg"
            subprocess.run(
                [program, "-y", "-i", file_path, output_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )


        log_conversion(history_file, date_time_str, file_path, target_format, output_path, program)

if __name__ == "__main__":
    mediaconvert()