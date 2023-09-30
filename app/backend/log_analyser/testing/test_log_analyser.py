import asyncio
from log_analyser.log_analyser import run_log_analyser
import os
import pytest


# VARIABLES
parent_directory: str = os.path.dirname(__file__)
test_files_path: str = f"{parent_directory}/.test_files/" 


# INTITIALISATION
def create_test_files_folder():
    # See if test_files_path exists
    if os.path.exists(test_files_path):
        return

    os.mkdir(test_files_path)

# log_analyser.py
@pytest.mark.asyncio
async def test_run_log_analyser():
    create_test_files_folder()

    # Test with a non-existent log file
    with pytest.raises(FileNotFoundError):
        await run_log_analyser(f"{test_files_path}nonexistent_file.txt")

    # Test with an empty log file
    empty_log_path = f"{test_files_path}empty_log.txt"
    with open(empty_log_path, "w"):
        pass
    await run_log_analyser(empty_log_path)

    # Test with a log file containing invalid log lines
    invalid_log_path = f"{test_files_path}invalid_log.txt"
    with open(invalid_log_path, "w") as log_file:
        log_file.write("Invalid log line 1\n")
        log_file.write("Invalid log line 2\n")
    await run_log_analyser(invalid_log_path)

    # Test with a log file containing a single valid log line
    valid_log_path = f"{test_files_path}valid_log.txt"
    with open(valid_log_path, "w") as log_file:
        log_file.write("log_id:123 | [LOG_TYPE] | [SOURCE] | 2023-09-30 12:34:56 | Log message\n")
    await run_log_analyser(valid_log_path)

    # Test with a log file containing multiple valid log lines
    multiple_logs_path = f"{test_files_path}multiple_logs.txt"
    with open(multiple_logs_path, "w") as log_file:
        log_file.write("log_id:123 | [LOG_TYPE] | [SOURCE] | 2023-09-30 12:34:56 | Log message 1\n")
        log_file.write("log_id:456 | [LOG_TYPE] | [SOURCE] | 2023-09-30 12:34:57 | Log message 2\n")
        log_file.write("log_id:789 | [LOG_TYPE] | [SOURCE] | 2023-09-30 12:34:58 | Log message 3\n")
    await run_log_analyser(multiple_logs_path)

    # Add assertions to validate the test results if needed