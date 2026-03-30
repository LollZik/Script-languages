import sys
import subprocess
from datetime import datetime
from fileinput import filename

from utils import *

def mediaconvert():
    if len(sys.argv) < 3:
        return

    input_dir = sys.argv[1]
    target_format = sys.argv[2]

    output_dir = get_output_dir()
    history_file = os.path.join(output_dir, "history.csv")

    files = find_media_files(input_dir)

    for file_path in files:
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d%H%M%S")
        date_time_str = now.strftime("%d-%m-%Y %H:%M:%S")

        filename = os.path.basename(file_path)
        name_without_ext, _ = os.path.splitext(filename)

        new_filename = f"{timestamp_str}-{name_without_ext}.{target_format}"
        output_path = os.path.join(output_dir, new_filename)


        # -y to overwrite existing files, -i to mark file_path as input
        # ffmpeg treats output_path as it's last argument and it doesn't have flags attached to it
        subprocess.run(
            ["ffmpeg", "-y", "-i", file_path, output_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        log_conversion(history_file, date_time_str, file_path, target_format, output_path)

if __name__ == "__main__":
    mediaconvert()