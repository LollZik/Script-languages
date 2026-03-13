import sys
from common import processLine

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

def main(process_line):
    line_count = 0
    empty_streak = 0
    preamble_possible = True
    preamble_skipped = False

    for line in sys.stdin:
        line = line.rstrip("\n")
        line_count += 1

        if line.strip() == "-----":
            return

        if not preamble_skipped and preamble_possible:
            if line.strip() == "":
                empty_streak += 1
            else:
                empty_streak = 0

            if empty_streak >= 2:
                preamble_skipped = True
                continue

            if line_count >= 10:
                preamble_possible = False

            continue

        processed = process_line(line)
        print(processed)


if __name__ == "__main__":
    main(processLine)