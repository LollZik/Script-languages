import sys
import csv
import io
from collections import Counter

def process_file():
    file_path = sys.stdin.read().strip()
    if not file_path:
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return

    # b)
    chars_count = len(content)
    words = content.split()
    words_count = len(words)
    lines_count = len(content.splitlines())

    most_freq_char = ""
    if chars_count > 0:
        most_freq_char = Counter(content).most_common(1)[0][0]

    most_freq_word = ""
    if words_count > 0:
        most_freq_word = Counter(words).most_common(1)[0][0]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        file_path,
        chars_count,
        words_count,
        lines_count,
        most_freq_char,
        most_freq_word
    ])
    print(output.getvalue().strip())

if __name__ == "__main__":
    process_file()