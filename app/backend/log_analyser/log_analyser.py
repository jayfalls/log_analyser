import asyncio
import sqlite3
import sys
import os
# IMPORT LOCALLY
## Get the directory path of the current script
current_script_dir: str = os.path.dirname(os.path.abspath(__file__))
## Get the parent directory path
parent_dir: str = os.path.dirname(current_script_dir)
## Add the parent directory to the import path
sys.path.append(parent_dir)
from log_analyser.components.sql_log import SQL_Log
from log_analyser.components.log_to_db import LogToDatabase


# PROGRAM START
async def run_log_analyser(log_path: str) -> None:
    log_database: SQL_Log = SQL_Log()
    log_database_error_check = await log_database.initialise_database()
    if log_database_error_check is None:
        print("Error: Failed to initialize the database.")
        return
    extractor: LogToDatabase = LogToDatabase()
    await extractor.log_to_database(log_database, log_path)
    log_database.close_database()