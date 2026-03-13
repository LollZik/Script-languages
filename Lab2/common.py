import sys

def processLine(line):
    if line.strip() == "":
        return ""
    return " ".join(line.split())