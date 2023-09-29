import asyncio
import sqlite3
from tests import default_tests


# VARIABLES
## Constants
DATABASE_PATH: str = "api_logs.db"
DATABASE_TABLES: set = {
    "log_id TEXT", 
    "log_type TEXT",
    "source TEXT",
    "date TEXT",
    "time TEXT", 
    "message TEXT"
    }

## Temp
test_log_path: str = ".test_files/API2023_09_27.txt"


# DATABASE
async def initialise_database():
    db_connection = sqlite3.connect(DATABASE_PATH)
    db_cursor = db_connection.cursor()

    # Create the table
    tables: str = ", ".join([str(table) for table in DATABASE_TABLES])
    db_cursor.execute(f"CREATE TABLE IF NOT EXISTS api_logs ({tables})")
    db_connection.commit()

    return db_connection    
    db_connection.close()


# Loading Files
async def clean_log_file(log_path: str) -> str:
    valid_logs: str = ""
    try:
        with open(log_path, 'r') as log_file:
            loop = asyncio.get_event_loop()
            tasks = []
            for line in log_file:
                if "[REPORTING]" not in line:
                   valid_logs += line
            return valid_logs
    except FileNotFoundError:
        return "Log File does not exist"


# PARSING
def split_log_line(log_line: str) -> list:
    return log_line.strip().split(" | ")

def parse_log_line(log_line: str) -> dict:
    items: list = split_log_line(log_line)
    
    log_id: str = items[0].split(":")[0]
    log_type: str = items[1].split("[")[1].split("]")[0]
    source: str = items[2].split("[")[1].split("]")[0]
    date, time = items[3].split(" ")
    message: str = items[4]
    
    return {
        "log_id": log_id,
        "log_type": log_type,
        "source": source,
        "date": date,
        "time": time,
        "log_type": log_type,
        "message": message,
    }


# PROGRAM START
async def start() -> None:
    db_connection = await initialise_database()
    logs: str = await clean_log_file(test_log_path)
    for log_line in logs.splitlines():
        print(parse_log_line(log_line))
        break


asyncio.run(start())