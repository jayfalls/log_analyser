import asyncio
from enum import Enum
import sqlite3
import sys
import os
from ..components.sql_log import SQL_Log


# VARIABLES
## Constants
### Errors
LOG_FILE_ERRORS: tuple = (
    "Log file does not exist",
    "Error occurred while reading the log file."
)
class LOG_FILE_ERROR_NAMES(Enum):
    FILE_NOT_FOUND: int = 0
    IO_ERROR: int = 1

class LogToDatabase():
    # LOADING FILES
    @staticmethod
    async def clean_log_file(log_path: str) -> str:
        valid_logs: str = ""
        try:
            with open(log_path, 'r') as log_file:
                for line in log_file:
                    line = line.strip()
                    if not line:
                        continue
                    if len(line) < 20: # I really shouldn't be using a random number here, but this is to make sure no empty lines are added
                        continue
                    if "[REPORTING]" not in line:
                        valid_logs += line + "\n"
                return valid_logs
        except FileNotFoundError:
            raise FileNotFoundError
            return LOG_FILE_ERRORS[LOG_FILE_ERROR_NAMES.FILE_NOT_FOUND.value]
        except IOError:
            raise IOError
            return LOG_FILE_ERRORS[LOG_FILE_ERROR_NAMES.IO_ERROR.value]

    # EXTRACTING
    @staticmethod
    def extract_log_line(log_line: str) -> dict:
        items: list = log_line.split(" | ")

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

    async def extract_log_to_database(self, log_database: SQL_Log, logs: str) -> None:
        for log_line in logs.splitlines():
            log_line_separated: dict = self.extract_log_line(log_line)
            if log_line_separated is None:
                print("Error: Failed to extract log line:", log_line)
                continue
            try:
                log_database.write_line_to_database(log_line_separated)
            except Exception as error:
                print("Error occurred while writing log line to database:", log_line)
                print("Error message:", str(error))
                raise error
                continue
        log_database.commit_to_database()
    
    async def log_to_database(self, log_database: SQL_Log, path_to_log: str) -> None:
        logs: str = await self.clean_log_file(path_to_log)
        if logs in LOG_FILE_ERRORS:
            print(logs)
            return
        try:
            await self.extract_log_to_database(log_database, logs)
        except Exception as error:
            print("Error occurred while extracting logs to the database:")
            raise error
            log_database.close_database()
            return