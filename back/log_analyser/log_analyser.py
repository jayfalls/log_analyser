import asyncio
import sqlite3


# VARIABLES
## Constants
DATABASE_PATH: str = "api_logs.db"
DATABASE_TABLE_NAME: str = "api_logs"
DATABASE_TABLE_NAMES: tuple = (
    "log_id", 
    "log_type",
    "source",
    "date",
    "time", 
    "message"
)

## Temp
test_log_path: str = ".test_files/API2023_09_27.txt"


# DATABASE
async def initialise_database():
    db_connection = sqlite3.connect(DATABASE_PATH)
    db_cursor = db_connection.cursor()

    # Create the table
    tables: str = " TEXT TRUE, ".join([str(table) for table in DATABASE_TABLE_NAMES])
    db_cursor.execute(f"CREATE TABLE IF NOT EXISTS {DATABASE_TABLE_NAME} ({tables})")
    commit_to_database(db_connection)

    return db_connection    
    db_connection.close()

def commit_to_database(db_connection) -> None:
    db_connection.commit()

def check_if_entry_exists(db_connection, log_line: dict) -> bool:
    db_cursor = db_connection.cursor()

    # Extract log_id, log_type, and time from log_line
    log_id: str = log_line.get("log_id")
    log_type: str = log_line.get("log_type")
    time: str = log_line.get("time")

    # Check if the data already exists in the database based on log_id, log_type, and time
    db_cursor.execute(f"SELECT log_id FROM {DATABASE_TABLE_NAME} WHERE log_id = ? AND log_type = ? AND time = ?", (log_id, log_type, time))
    does_exist: bool = db_cursor.fetchone()

    return does_exist

def write_line_to_database(db_connection, log_line: dict) -> None:
    if check_if_entry_exists(db_connection, log_line):
        return
    
    db_cursor = db_connection.cursor()
    # Insert the data into the table
    tables_string: str = ", ".join(str(table) for table in DATABASE_TABLE_NAMES)
    values_string: str = ", ".join([f":{str(table)}" for table in DATABASE_TABLE_NAMES])
    db_cursor.execute(f"INSERT INTO {DATABASE_TABLE_NAME} ({tables_string}) VALUES ({values_string})", log_line)


# Loading Files
async def clean_log_file(log_path: str) -> str:
    valid_logs: str = ""
    try:
        with open(log_path, 'r') as log_file:
            loop = asyncio.get_event_loop()
            tasks = []
            for line in log_file:
                if len(line) < 20: # Shouldn't be using a random number here, this is to make sure no empty lines are added
                    continue
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

async def parse_log_to_database(db_connection, logs: str) -> None:
    loop = asyncio.get_event_loop()
    for log_line in logs.splitlines():
        log_line_seperated: dict = parse_log_line(log_line)
        write_line_to_database(db_connection, log_line_seperated)
    commit_to_database(db_connection)   


# PROGRAM START
async def start() -> None:
    db_connection = await initialise_database()
    logs: str = await clean_log_file(test_log_path)
    await parse_log_to_database(db_connection, logs)


asyncio.run(start())