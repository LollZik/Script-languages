from readLog import read_log


def detect_sus(log, threshold):
    counts = {}
    error_counts = {}

    for entry in log:
        ip = entry[2]
        status = entry[9]

        if ip in counts:
            counts[ip] += 1
        else:
            counts[ip] = 1

        if status == 404:
            if ip in error_counts:
                error_counts[ip] += 1
            else:
                error_counts[ip] = 1

    sus_ips = []
    for ip in counts:
        total = counts[ip]
        errors = error_counts.get(ip, 0)

        if total > threshold and errors > 0:
            sus_ips.append(ip)
    return sus_ips

def main():
    data = read_log()
    log = detect_sus(data, 3000)
    print(log)

if __name__ == "__main__":
    main()