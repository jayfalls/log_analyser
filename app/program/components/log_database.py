from enum import Enum
import os
import sqlite3

# VARIABLES
## References
script_path: str = os.path.abspath(__file__)
directory_path: str = os.path.dirname(script_path)
## Constants
### Normal
DATABASE_PATH = os.path.join(directory_path, "api_logs.db")
DATABASE_TABLE_NAME: str = "api_logs"
DATABASE_TABLE_NAMES: tuple = (
    "log_id", 
    "log_type",
    "source",
    "date",
    "time", 
    "message"
)
class DATABASE_TABLE_INDEXES(Enum):
    LOG_ID: int = 0
    LOG_TYPE: int = 1
    SOURCE: int = 2
    DATE: int = 3
    TIME: int = 4
    MESSAGE: int = 5
### Debug
test_files_path = os.path.join(directory_path, ".test_files/")
def create_test_files_folder():
    # See if test_files_path exists
    if os.path.exists(test_files_path):
        return

    os.mkdir(test_files_path)
create_test_files_folder()
DEBUG_DATABASE_PATH = os.path.join(test_files_path, "api_logs.db")


# HELPER FUNCTIONS
def get_table_filter(table_name: str, tables_values: set) -> str:
    if not table_name:
        raise Exception("SQL Error: Table name cannot be empty")
    if not len(tables_values) > 0:
        raise Exception(f"SQL Error: Table filter {table_name} can't be empty!")
    return f"WHERE {table_name} IN ({tables_values}) "

def add_date_filter(date_range: tuple, existing_filter: str = "") -> str:
    if len(date_range) != 2:
        raise ValueError("Date filters should each be a tuple of (start, end)")
    start_date, end_date = date_range
    if not isinstance(start_date, str) or not isinstance(end_date, str):
        raise ValueError("Date filters should be strings.")
    return f"{existing_filter}AND date BETWEEN ? AND ? ", (date_range[0], date_range[1])

def add_time_filter(time_range: tuple, existing_filter: str = "") -> str:
    if len(time_range) != 2:
        raise ValueError("Time filters should each be a tuple of (start, end)")
    start_time, end_time = time_range
    if not isinstance(start_time, str) or not isinstance(end_time, str):
        raise ValueError("Time filters should be strings.")
    return f"{existing_filter}AND time BETWEEN ? AND ? ", (time_range[0], time_range[1])

def inject_filters(filters: tuple) -> str:
    filter_prompt: str = ""
    filters_length: int = len(filters)
    if not 0 < filters_length <= 3:
        return ""
    for index, filter in enumerate(filters):
        if index == 0:
            filter_prompt = get_table_filter(DATABASE_TABLE_NAMES[DATABASE_TABLE_INDEXES.LOG_ID.value], filter)
            continue
        if index == 1:
            filter_prompt += add_date_filter(filter, filter_prompt)
            continue
        filter_prompt += add_time_filter(filter, filter_prompt)
    if filter_prompt == "":
        raise Exception("Error: Unknown input to inject_filters()")
    return filter_prompt


class LogDatabase():
    # VARIABLES
    ## References
    database_connection: sqlite3.Connection
    ## States
    debug_mode: bool = False
    filters: tuple = () # (log_ids, (start_date, end_date), (start_time, end_time))

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
    def get_path(self) -> str:
        if self.debug_mode:
            return DEBUG_DATABASE_PATH
        else:
            return DATABASE_PATH
    
    def does_database_exist(self) -> bool:
        database_path: str = self.get_path()
        return os.path.exists(database_path)
        
    ## Access
    def initialise_database(self) -> None:
        database_path: str = self.get_path()
        try:
            # Use context manager to automatically close the connection
            with sqlite3.connect(database_path) as new_database_connection:
                self.database_connection = new_database_connection
                database_cursor: sqlite3.Cursor = new_database_connection.cursor()

                # Create the table
                tables: str = " TEXT TRUE, ".join([str(table) for table in DATABASE_TABLE_NAMES])
                database_cursor.execute(f"CREATE TABLE IF NOT EXISTS {DATABASE_TABLE_NAME} ({tables})")
                self.commit_to_database()

                return
        except sqlite3.Error as error:
            self.handle_sql_error(error)
            raise error
    
    def close_database(self) -> None:
        try:
            self.database_connection.close()
        except sqlite3.Error as error:
            self.handle_sql_error(error)
            raise error
    
    def clear_database(self) -> None:
        self.close_database()
        database_path: str = self.get_path()
        try:
            os.remove(database_path)
            print(f"Database '{database_path}' deleted successfully.")
        except OSError as e:
            print(f"Error deleting file '{database_path}': {str(e)}")

    def commit_to_database(self) -> None:
        try:
            self.database_connection.commit()
        except sqlite3.Error as error:
            self.handle_sql_error(error)
            raise error
    
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
            self.handle_sql_error(error)
            raise error
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
            self.handle_sql_error(error)
            raise error
    
    ## Querying
    def get_all_logs(self) -> tuple:
        try:
            database_cursor: sqlite3.Cursor = self.database_connection.cursor()
            database_cursor.execute(f"SELECT log_type, date, time, source, message  FROM api_logs {inject_filters(self.filters)}GROUP BY time")
            results: tuple = database_cursor.fetchall()
            new_results: list = []
            for result in results:
                new_results.append(" ".join(result))
            return new_results
        except sqlite3.Error as error:
            self.handle_sql_error(error)
            raise error
            return None

    def get_log_type_frequencies(self) -> tuple:
        try:
            database_cursor: sqlite3.Cursor = self.database_connection.cursor()
            database_cursor.execute(f"SELECT log_type, COUNT(*) AS log_count FROM api_logs {inject_filters(self.filters)}GROUP BY log_type ORDER BY log_count ASC")
            results: tuple = database_cursor.fetchall()
            return results
        except sqlite3.Error as error:
            self.handle_sql_error(error)
            raise error
            return None
    
    def get_source_frequencies(self) -> tuple:
        try:
            database_cursor: sqlite3.Cursor = self.database_connection.cursor()
            database_cursor.execute(f"SELECT source, COUNT(*) AS source_count FROM api_logs {inject_filters(self.filters)}GROUP BY source ORDER BY source_count ASC")
            results: tuple = database_cursor.fetchall()
            return results
        except sqlite3.Error as error:
            self.handle_sql_error(error)
            raise error
            return None
    
    def get_sorted_log_types(self) -> dict:
        try:
            database_cursor: sqlite3.Cursor = self.database_connection.cursor()
            database_cursor.execute(f"SELECT log_type, message, date, time FROM api_logs {inject_filters(self.filters)}ORDER BY message, date, time")
            results: tuple = database_cursor.fetchall()

            log_types: dict = {}
            for result in results:
                log_type: str = result[0]
                if log_type not in log_types:
                    log_types[log_type] = []
                log_types[log_type].append(result[1:])
            return log_types
        except sqlite3.Error as error:
            self.handle_sql_error(error)
            raise error
            return None
    
    def get_sorted_sources(self) -> dict:
        try:
            database_cursor: sqlite3.Cursor = self.database_connection.cursor()
            database_cursor.execute(f"SELECT source, message, date, time FROM api_logs {inject_filters(self.filters)}ORDER BY message, date, time")
            results: tuple = database_cursor.fetchall()

            sources: dict = {}
            for result in results:
                source: str = result[0]
                if source not in sources:
                    sources[source] = []
                sources[source].append(result[1:])
            return sources
        except sqlite3.Error as error:
            self.handle_sql_error(error)
            raise error
            return None