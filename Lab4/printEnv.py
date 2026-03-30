import os
import sys

def filter_env():
    if sys.argv.__len__() > 1:
        criteria = sys.argv[1:]
        result = {}
        for c in criteria:
            for k, v in os.environ.items():
                if c.lower() in k.lower():
                    result[k] = v
        return sorted(result.items())
    else:
        return sorted(os.environ.items())

def main():
    result = print_env()
    print(result)

if __name__ == "__main__":
    main()