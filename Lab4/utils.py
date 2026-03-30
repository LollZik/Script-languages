import os
import csv

def get_output_dir():
    target_dir = os.environ.get("CONVERTED_DIR", os.path.join(os.getcwd(), "converted"))
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

def find_media_files(directory):
    media_files = []
    valid_extensions = ('.mp4', '.avi', '.mkv', '.mov', '.mp3', '.wav', '.flac', '.webm', '.ogg', '.wmv')

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(valid_extensions):
                media_files.append(os.path.join(root, file))
    return media_files

def log_conversion(history_path, conversion_time, original_path, target_format, output_path):
    file_exists = os.path.exists(history_path)
    with open(history_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["conversion_datetime", "original_path", "target_format", "output_path"])
        writer.writerow([conversion_time, original_path, target_format, output_path])