from readLog import read_log


def get_extension_stats(log):
    stats = {}
    for entry in log:
        uri = entry[8].split('?')[0]

        if '.' in uri:
            parts = uri.split('.')
            extension = parts[-1]
            if len(extension) <= 5 and extension.isalnum():
                if extension in stats:
                    stats[extension] += 1
                else:
                    stats[extension] = 1
    return stats

def main():
    data = read_log()
    log = get_extension_stats(data)
    print(log)

if __name__ == "__main__":
    main()