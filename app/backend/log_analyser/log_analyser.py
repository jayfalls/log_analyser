import asyncio
import sqlite3
import sys
import os
from .interfaces.log_analysis_tools import LogTools


# VARIABLES
## References
log_tools: LogTools
## States
debug_mode: bool = False


# LOG INTERACTION
def start_log_analyser() -> None:
    global log_tools
    log_tools = LogTools()
    log_tools.debug_mode = debug_mode

## Input
async def import_logs(log_paths: tuple) -> None:
    await log_tools.import_logs(log_paths)

## Output
def analyse(filters: tuple = ()) -> tuple:
    return log_tools.analyse()


# DEBUG
## DEBUG VARIABLES
test_log_path1: str = "log_analyser/.test_files/API2023_09_24.log"
test_log_path2: str = "log_analyser/.test_files/API2023_09_27.log"
## DEBUG FUNCTIONS
async def load_test_logs() -> None:
    start_log_analyser()
    log_paths: tuple = (test_log_path2,)
    await import_logs(log_paths)
    analyse()
