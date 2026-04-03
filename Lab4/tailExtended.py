import sys
import time
import os
from collections import deque

def process_text(n, follow, source, reverse, is_chars):
    if is_chars:
        text = list(source.read())
        text.reverse()
        last = list()
        for char in text:
            last.append(char)
            n = n-1
            if n == 0:
                last.reverse()
                break
    else:
        last = list(deque(source, maxlen=n))
    if reverse:
        last.reverse()

    for line in last:
        print(line, end='')

    if follow:
        try:
            while True:
                line = source.readline()
                if line:
                    print(line, end='')
                else:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    if source is not sys.stdin:
        source.close()

def read_args():
    n = 10
    follow = False
    file_path = ""
    reverse = bool(os.environ["TAIL_REVERSE"])
    is_chars = False
    if (os.environ["TAIL_MODE"]=="chars"):
        is_chars = True

    for arg in sys.argv[1:]:
        if arg.startswith('--lines='):
            try:
                n = int(arg.split('=')[1])
            except (IndexError, ValueError):
                print("Error: Wrong format --lines=n")
                sys.exit(1)
        elif arg == '--follow':
            follow = True
        else:
            file_path = arg

    try:
        if file_path:
            f = open(file_path, 'r', encoding='utf-8')
        else:
            f = sys.stdin
    except Exception as e:
        print(f"Error: Couldn't open the file")
        exit(1)

    process_text(n, follow, f, reverse, is_chars)


def main():
    read_args()

if __name__ == "__main__":
    main()