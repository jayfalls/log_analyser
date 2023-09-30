import asyncio
import sqlite3
import sys
import os
from .components.sql_log import SQL_Log
from .components.log_to_db import LogToDatabase


# PROGRAM START
async def run_log_analyser(log_path: str) -> None:
    log_database: SQL_Log = SQL_Log()
    log_database_error_check = await log_database.initialise_database()
    if log_database_error_check is None:
        raise Exception("Error: Failed to initialize the database.")
        return
    extractor: LogToDatabase = LogToDatabase()
    await extractor.log_to_database(log_database, log_path)
    log_database.close_database()