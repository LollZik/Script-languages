from datetime import datetime

def read_log_file(filepath):
    log_data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                fields = line.split('\t')
                try:
                    ts = datetime.fromtimestamp(float(fields[0]))
                    uid = fields[1]
                    orig_h = fields[2]
                    orig_p = int(fields[3])
                    resp_h = fields[4]
                    resp_p = int(fields[5])
                    method = fields[7]
                    host = fields[8]
                    uri = fields[9]
                    status = int(fields[14]) if fields[14] != '-' else 0

                    formatted_line = f"{orig_h} - [{ts.strftime('%d/%b/%Y:%H:%M:%S')}] \"{method} {uri}\" {status}"

                    master_text = formatted_line
                    if len(master_text) > 60:
                        master_text = master_text[:60] + "..."

                    log_entry = {
                        "master_text": master_text,
                        "remote_host": orig_h,
                        "date": ts.strftime('%Y-%m-%d'),
                        "time": ts.strftime('%H:%M:%S'),
                        "method": method,
                        "resource": uri,
                        "status": str(status)
                    }
                    log_data.append(log_entry)
                except (ValueError, IndexError):
                    continue

    except Exception as e:
        return None, str(e)

    return log_data, None