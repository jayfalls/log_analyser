import asyncio
from enum import Enum
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
### Errors
LOG_FILE_ERRORS: tuple = (
    "Log File does not exist",
    "Error occurred while reading the log file."
)
class LOG_FILE_ERROR_NAMES(Enum):
    FILE_NOT_FOUND = 0
    IO_ERROR = 1

## Temp
test_log_path: str = ".test_files/API2023_09_27.txt"


# ERROR HANDLING
def print_sql_error(e) -> None:
    print(f"An error occurred while initializing the database: {e}")

# DATABASE
async def initialise_database() -> sqlite3.Connection:
    try:
        db_connection = sqlite3.connect(DATABASE_PATH)
        db_cursor: sqlite3.Cursor = db_connection.cursor()

        # Create the table
        tables: str = " TEXT TRUE, ".join([str(table) for table in DATABASE_TABLE_NAMES])
        db_cursor.execute(f"CREATE TABLE IF NOT EXISTS {DATABASE_TABLE_NAME} ({tables})")
        commit_to_database(db_connection)

        return db_connection
    except sqlite3.Error as error:
        print_sql_error(error)
        return None

def commit_to_database(db_connection: sqlite3.Connection) -> None:
    try:
        db_connection.commit()
    except sqlite3.Error as error:
        print_sql_error(error)

def check_if_entry_exists(db_connection: sqlite3.Connection, log_line: dict) -> bool:
    try:
        db_cursor: sqlite3.Cursor = db_connection.cursor()

        # Extract log_id, log_type, and time from log_line
        log_id: str = log_line.get("log_id")
        log_type: str = log_line.get("log_type")
        time: str = log_line.get("time")

        # Check if the data already exists in the database based on log_id, log_type, and time
        db_cursor.execute(f"SELECT log_id FROM {DATABASE_TABLE_NAME} WHERE log_id = ? AND log_type = ? AND time = ?", (log_id, log_type, time))
        does_exist: bool = db_cursor.fetchone()

        return does_exist
    except sqlite3.Error as error:
        print_sql_error(error)
        return False

def write_line_to_database(db_connection: sqlite3.Connection, log_line: dict) -> None:
    try:
        if check_if_entry_exists(db_connection, log_line):
            return

        db_cursor: sqlite3.Cursor = db_connection.cursor()
        # Insert the data into the table
        tables_string: str = ", ".join(str(table) for table in DATABASE_TABLE_NAMES)
        values_string: str = ", ".join([f":{str(table)}" for table in DATABASE_TABLE_NAMES])
        db_cursor.execute(f"INSERT INTO {DATABASE_TABLE_NAME} ({tables_string}) VALUES ({values_string})", log_line)
    except sqlite3.Error as error:
        print_sql_error(error)
        return False

def close_database(db_connection: sqlite3.Connection) -> None:
    try:
        db_connection.close()
    except sqlite3.Error as error:
        print_sql_error(error)
        return False


# LOADING FILES
async def clean_log_file(log_path: str) -> str:
    valid_logs: str = ""
    try:
        with open(log_path, 'r') as log_file:
            for line in log_file:
                line = line.strip()
                if not line:
                    continue
                if len(line) < 5: # Shouldn't be using a random number here, this is to make sure no empty lines are added
                    continue
                if "[REPORTING]" not in line:
                    valid_logs += line + "\n"
            return valid_logs
    except FileNotFoundError:
        return LOG_FILE_ERRORS[LOG_FILE_ERROR_NAMES.FILE_NOT_FOUND]
    except IOError:
        return LOG_FILE_ERRORS[LOG_FILE_ERROR_NAMES.IO_ERROR]


# PARSING
def split_log_line(log_line: str) -> list:
    return log_line.split(" | ")

def parse_log_line(log_line: str) -> dict:
    items: list = split_log_line(log_line)

    if len(items) != 5:
        return None

    # If log_id isn't seperated by an api call, return error
    log_id_parts: tuple = items[0].split(":")
    if len(log_id_parts) != 2:
        return None
    log_id: str = log_id_parts[0]

    log_type: str = items[1].split("[")[1].split("]")[0]
    source: str = items[2].split("[")[1].split("]")[0]

    # If date and time aren't in a single block, return error
    date_time_parts: tuple = items[3].split(" ")
    if len(date_time_parts) != 2:
        return None
    date, time = date_time_parts

    message: str = items[4]

    return {
        "log_id": log_id,
        "log_type": log_type,
        "source": source,
        "date": date,
        "time": time,
        "message": message,
    }

async def parse_log_to_database(db_connection, logs: str) -> None:
    loop = asyncio.get_event_loop()
    for log_line in logs.splitlines():
        log_line_seperated: dict = parse_log_line(log_line)
        if log_line_seperated == None:
            return
        write_line_to_database(db_connection, log_line_seperated)
    commit_to_database(db_connection)   

async def parse_log_to_database(db_connection, logs: str) -> None:
    loop = asyncio.get_event_loop()
    for log_line in logs.splitlines():
        log_line_separated: dict = parse_log_line(log_line)
        if log_line_separated is None:
            print("Error: Failed to parse log line:", log_line)
            continue
        try:
            write_line_to_database(db_connection, log_line_separated)
        except Exception as e:
            print("Error occurred while writing log line to database:", log_line)
            print("Error message:", str(e))
            continue
    commit_to_database(db_connection)


# PROGRAM START
async def start() -> None:
    db_connection = await initialise_database()
    logs: str = await clean_log_file(test_log_path)
    if logs in LOG_FILE_ERRORS:
        print(logs)
        return
    await parse_log_to_database(db_connection, logs)
    close_database(db_connection)

async def start() -> None:
    db_connection = await initialise_database()
    if db_connection is None:
        print("Error: Failed to initialize the database.")
        return

    logs: str = await clean_log_file(test_log_path)
    if logs in LOG_FILE_ERRORS:
        print(logs)
        return

    try:
        await parse_log_to_database(db_connection, logs)
    except Exception as e:
        print("Error occurred while parsing logs to the database:")
        print("Error message:", str(e))
        close_database(db_connection)
        return

    close_database(db_connection)


asyncio.run(start())