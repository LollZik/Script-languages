import sys
from database import DatabaseManager

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    db_name = sys.argv[1]

    try:
        manager = DatabaseManager(db_name)
        manager.create_tables()
    except Exception as e:
        print(f"Error occured: {e}")
        sys.exit(1)