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

create_test_files_folder()

# TESTS
@pytest.mark.asyncio
async def test_run_log_analyser_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        await run_log_analyser(f"{test_files_path}nonexistent_file.log")

@pytest.mark.asyncio
async def test_run_log_analyser_empty_log():
    empty_log_path = f"{test_files_path}empty_log.log"
    with open(empty_log_path, "w"):
        pass
    await run_log_analyser(empty_log_path)

@pytest.mark.asyncio
async def test_run_log_analyser_invalid_log():
    invalid_log_path = f"{test_files_path}invalid_log.log"
    with open(invalid_log_path, "w") as log_file:
        log_file.write("Invalid log line 1\n")
        log_file.write("Invalid log line 2\n")
    await run_log_analyser(invalid_log_path)

@pytest.mark.asyncio
async def test_run_log_analyser_single_valid_log():
    valid_log_path = f"{test_files_path}valid_log.log"
    with open(valid_log_path, "w") as log_file:
        log_file.write("log_id:123 | [LOG_TYPE] | [SOURCE] | 2023-09-30 12:34:56.579289 | Log message\n")
    await run_log_analyser(valid_log_path)

@pytest.mark.asyncio
async def test_run_log_analyser_multiple_valid_logs():
    multiple_logs_path = f"{test_files_path}multiple_logs.log"
    with open(multiple_logs_path, "w") as log_file:
        log_file.write("log_id:123 | [LOG_TYPE] | [SOURCE] | 2023-09-30 12:34:56.579289 | Log message 1\n")
        log_file.write("log_id:456 | [LOG_TYPE] | [SOURCE] | 2023-09-30 12:34:57.579300 | Log message 2\n")
        log_file.write("log_id:789 | [LOG_TYPE] | [SOURCE] | 2023-09-30 12:34:58.579350 | Log message 3\n")
    await run_log_analyser(multiple_logs_path)


# Test with invalid file types
@pytest.mark.asyncio
async def test_invalid_file_types():
    invalid_file_path = f"{test_files_path}invalid_file.pdf" 
    with open(invalid_file_path, "wb") as invalid_file:
        invalid_file.write(b"Invalid PDF file")

    with pytest.raises(TypeError):
        await run_log_analyser(invalid_file_path)


# Test with a log file containing invalid line structures
@pytest.mark.asyncio  
async def test_invalid_line_structures():
    invalid_structure_path = f"{test_files_path}invalid_structure.log"
    with open(invalid_structure_path, "w") as invalid_file:
        invalid_file.write("missing pipe symbol\n")
        invalid_file.write("too | many | pipes\n")
    
    await run_log_analyser(invalid_structure_path)
    # Assert errors logged for invalid lines


# Test with incorrect date formats
@pytest.mark.asyncio
async def test_incorrect_date_formats():
    invalid_date_path = f"{test_files_path}invalid_dates.log"
    with open(invalid_date_path, "w") as invalid_file:
        invalid_file.write("log_id:123 | [LOG_TYPE] | [SOURCE] | 20230930 12:34:56 | Log\n")
        invalid_file.write("log_id:456 | [LOG_TYPE] | [SOURCE] | 2002-30-09 12:34:56 | Log\n")
    
    with pytest.raises(ValueError):
        await run_log_analyser(invalid_date_path)
    # Assert errors logged for invalid dates


# Test with missing required fields  
@pytest.mark.asyncio
async def test_missing_required_fields():
    missing_fields_path = f"{test_files_path}missing_fields.log"
    with open(missing_fields_path, "w") as invalid_file:
        invalid_file.write("log_id:123 |  | [SOURCE] | 2023-09-30 12:34:56 | Log\n")
        invalid_file.write("log_id:456 | [LOG_TYPE] |  | 2023-09-30 12:34:56 | Log\n")

    await run_log_analyser(missing_fields_path)
    # Assert errors logged for missing fields


# Test with unexpected special characters
@pytest.mark.asyncio
async def test_unexpected_characters():
    invalid_chars_path = f"{test_files_path}invalid_chars.log"
    with open(invalid_chars_path, "w") as invalid_file:
        invalid_file.write("log_id:123 | [LOG#!] | [SOURCE] | 2023-09-30 12:34:56.579289 | Log\n")
    
    await run_log_analyser(invalid_chars_path)
    # Assert errors logged for unexpected chars  


# Test with excessively long log lines
@pytest.mark.asyncio
async def test_long_log_lines():
    long_log_path = f"{test_files_path}long_logs.log"
    with open(long_log_path, "w") as invalid_file:
        invalid_file.write("x" * 500 + "\n")

    await run_log_analyser(long_log_path)
    # Assert errors logged for long lines