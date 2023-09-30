import asyncio
import os
import sqlite3


# VARIABLES
## References
script_path: str = os.path.abspath(__file__)
directory_path: str = os.path.dirname(script_path)
## States
debug_mode = False
## Constants
### Normal
DATABASE_PATH: str = f"{directory_path}/api_logs.db"
DATABASE_TABLE_NAME: str = "api_logs"
DATABASE_TABLE_NAMES: tuple = (
    "log_id", 
    "log_type",
    "source",
    "date",
    "time", 
    "message"
)
### Debug
test_files_path: str = f"{directory_path}/.test_files/"
def create_test_files_folder():
    # See if test_files_path exists
    if os.path.exists(test_files_path):
        return

    os.mkdir(test_files_path)
create_test_files_folder()
DEBUG_DATABASE_PATH: str = f"{test_files_path}api_logs.db"


class SQL_Log():
    # VARIABLES
    ## References
    database_connection: sqlite3.Connection

    # ERROR HANDLING
    @staticmethod
    def handle_sql_error(error: sqlite3.Error) -> None:
        error_message = str(error)
        if "UNIQUE constraint failed" in error_message:
            print("Error: Unique constraint violated.")
        elif "FOREIGN KEY constraint failed" in error_message:
            print("Error: Foreign key constraint violated.")
        else:
            print("An error occurred while initializing the database:", error_message)

    # DATABASE
    async def initialise_database(self) -> sqlite3.Connection:
        database_path: str = ""
        if self.debug_mode:
            database_path = DEBUG_DATABASE_PATH
        else:
            database_path = DATABASE_PATH
        try:
            # Use context manager to automatically close the connection
            with sqlite3.connect(database_path) as new_database_connection:
                self.database_connection = new_database_connection
                database_cursor: sqlite3.Cursor = new_database_connection.cursor()

                # Create the table
                tables: str = " TEXT TRUE, ".join([str(table) for table in DATABASE_TABLE_NAMES])
                database_cursor.execute(f"CREATE TABLE IF NOT EXISTS {DATABASE_TABLE_NAME} ({tables})")
                self.commit_to_database()

                return new_database_connection
        except sqlite3.Error as error:
            raise error
            self.handle_sql_error(error)
            return None

    def commit_to_database(self) -> None:
        try:
            self.database_connection.commit()
        except sqlite3.Error as error:
            raise error
            self.handle_sql_error(error)

    def check_if_entry_exists(self, log_line: dict) -> bool:
        try:
            database_cursor: sqlite3.Cursor = self.database_connection.cursor()

            # Extract log_id, log_type, and time from log_line
            log_id: str = log_line.get("log_id")
            log_type: str = log_line.get("log_type")
            time: str = log_line.get("time")

            # Check if the data already exists in the database based on log_id, log_type, and time
            database_cursor.execute(f"SELECT log_id FROM {DATABASE_TABLE_NAME} WHERE log_id = ? AND log_type = ? AND time = ?", (log_id, log_type, time))
            does_exist: bool = database_cursor.fetchone()

            return does_exist
        except sqlite3.Error as error:
            raise error
            self.handle_sql_error(error)
            return False

    def write_line_to_database(self, log_line: dict) -> None:
        try:
            if self.check_if_entry_exists(log_line):
                return

            database_cursor: sqlite3.Cursor = self.database_connection.cursor()
            # Insert the data into the table
            tables_string: str = ", ".join(str(table) for table in DATABASE_TABLE_NAMES)
            values_string: str = ", ".join([f":{str(table)}" for table in DATABASE_TABLE_NAMES])
            database_cursor.execute(f"INSERT INTO {DATABASE_TABLE_NAME} ({tables_string}) VALUES ({values_string})", log_line)
        except sqlite3.Error as error:
            raise error
            self.handle_sql_error(error)
            return False

    def close_database(self) -> None:
        try:
            self.database_connection.close()
        except sqlite3.Error as error:
            raise error
            self.handle_sql_error(error)
            return False