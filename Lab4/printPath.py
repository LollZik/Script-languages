import os

def print_catalogs():
    for path in os.environ['PATH'].split(os.pathsep):
        if path:
            print(path)
            print_executables(path)

def print_executables(path):
    try:
        for e in os.listdir(path):
            if e.endswith(('.exe', '.bat', '.com')):
                print(e)
    except PermissionError:
        print(f"Error: Permission denied")
    except FileNotFoundError:
        print(f"Error: There is no catalog with this name")

def main():
    print_catalogs()

if __name__ == "__main__":
    main()