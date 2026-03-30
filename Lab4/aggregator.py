import sys
import os
import csv
import subprocess
import io
from collections import Counter

def aggregate():
    if len(sys.argv) < 2:
        return

    directory = sys.argv[1]
    results = []

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            process = subprocess.run(
                ['python', 'fileToCsv.py'],
                input=file_path,
                text=True,
                capture_output=True
            )

            if process.stdout:
                try:
                    reader = csv.reader(io.StringIO(process.stdout.strip()))
                    for row in reader:
                        if len(row) == 6:
                            data = {
                                "file_path": row[0],
                                "total_characters": int(row[1]),
                                "total_words": int(row[2]),
                                "total_lines": int(row[3]),
                                "most_frequent_character": row[4],
                                "most_frequent_word": row[5]
                            }
                            results.append(data)
                except Exception:
                    pass

    total_files = len(results)
    total_chars = sum(r.get("total_characters", 0) for r in results)
    total_words = sum(r.get("total_words", 0) for r in results)
    total_lines = sum(r.get("total_lines", 0) for r in results)

    all_chars = [r.get("most_frequent_character") for r in results if r.get("most_frequent_character")]
    all_words = [r.get("most_frequent_word") for r in results if r.get("most_frequent_word")]

    overall_freq_char = Counter(all_chars).most_common(1)[0][0] if all_chars else ""
    overall_freq_word = Counter(all_words).most_common(1)[0][0] if all_words else ""

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "total_files",
        "total_characters",
        "total_words",
        "total_lines",
        "most_frequent_character",
        "most_frequent_word"
    ])
    writer.writerow([
        total_files,
        total_chars,
        total_words,
        total_lines,
        overall_freq_char,
        overall_freq_word
    ])

    print(output.getvalue().strip())


if __name__ == "__main__":
    aggregate()