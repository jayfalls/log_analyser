import asyncio
import server
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
async def test_log_analyser_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        test_path: set = set()
        test_path.add(f"{test_files_path}nonexistent_file.log")
        await server.import_logs(test_path)

@pytest.mark.asyncio
async def test_log_analyser_empty_log():
    empty_log_path = f"{test_files_path}empty_log.log"
    with open(empty_log_path, "w"):
        pass
    test_path: set = set()
    test_path.add(empty_log_path)
    await server.import_logs(test_path)

@pytest.mark.asyncio
async def test_log_analyser_invalid_log():
    invalid_log_path = f"{test_files_path}invalid_log.log"
    with open(invalid_log_path, "w") as log_file:
        log_file.write("Invalid log line 1\n")
        log_file.write("Invalid log line 2\n")
    test_path: set = set()
    test_path.add(invalid_log_path)
    await server.import_logs(test_path)

@pytest.mark.asyncio
async def test_log_analyser_single_valid_log():
    valid_log_path = f"{test_files_path}valid_log.log"
    with open(valid_log_path, "w") as log_file:
        log_file.write("log_id:123 | [LOG_TYPE] | [SOURCE] | 2023-09-30 12:34:56.579289 | Log message\n")
    test_path: set = set()
    test_path.add(valid_log_path)
    await server.import_logs(test_path)

@pytest.mark.asyncio
async def test_log_analyser_multiple_valid_logs():
    multiple_logs_path = f"{test_files_path}multiple_logs.log"
    with open(multiple_logs_path, "w") as log_file:
        log_file.write("log_id:123 | [LOG_TYPE] | [SOURCE] | 2023-09-30 12:34:56.579289 | Log message 1\n")
        log_file.write("log_id:456 | [LOG_TYPE] | [SOURCE] | 2023-09-30 12:34:57.579300 | Log message 2\n")
        log_file.write("log_id:789 | [LOG_TYPE] | [SOURCE] | 2023-09-30 12:34:58.579350 | Log message 3\n")
    test_path: set = set()
    test_path.add(multiple_logs_path)
    await server.import_logs(test_path)


# Test with invalid file types
@pytest.mark.asyncio
async def test_invalid_file_types():
    invalid_file_path = f"{test_files_path}invalid_file.pdf" 
    with open(invalid_file_path, "wb") as invalid_file:
        invalid_file.write(b"Invalid PDF file")

    with pytest.raises(TypeError):
        test_path: set = set()
        test_path.add(invalid_file_path)
        await server.import_logs(test_path)


# Test with a log file containing invalid line structures
@pytest.mark.asyncio  
async def test_invalid_line_structures():
    invalid_structure_path = f"{test_files_path}invalid_structure.log"
    with open(invalid_structure_path, "w") as invalid_file:
        invalid_file.write("missing pipe symbol\n")
        invalid_file.write("too | many | pipes\n")
    
    test_path: set = set()
    test_path.add(invalid_structure_path)
    await server.import_logs(test_path)


# Test with incorrect date formats
@pytest.mark.asyncio
async def test_incorrect_date_formats():
    invalid_date_path = f"{test_files_path}invalid_dates.log"
    with open(invalid_date_path, "w") as invalid_file:
        invalid_file.write("log_id:123 | [LOG_TYPE] | [SOURCE] | 20230930 12:34:56 | Log\n")
        invalid_file.write("log_id:456 | [LOG_TYPE] | [SOURCE] | 2002-30-09 12:34:56 | Log\n")
    
    with pytest.raises(ValueError):
        test_path: set = set()
        test_path.add(invalid_date_path)
        await server.import_logs(test_path)


# Test with missing required fields  
@pytest.mark.asyncio
async def test_missing_required_fields():
    missing_fields_path = f"{test_files_path}missing_fields.log"
    with open(missing_fields_path, "w") as invalid_file:
        invalid_file.write("log_id:123 |  | [SOURCE] | 2023-09-30 12:34:56 | Log\n")
        invalid_file.write("log_id:456 | [LOG_TYPE] |  | 2023-09-30 12:34:56 | Log\n")

    test_path: set = set()
    test_path.add(missing_fields_path)
    await server.import_logs(test_path)


# Test with unexpected special characters
@pytest.mark.asyncio
async def test_unexpected_characters():
    invalid_chars_path = f"{test_files_path}invalid_chars.log"
    with open(invalid_chars_path, "w") as invalid_file:
        invalid_file.write("log_id:123 | [LOG#!] | [SOURCE] | 2023-09-30 12:34:56.579289 | Log\n")
    
    test_path: set = set()
    test_path.add(invalid_chars_path)
    await server.import_logs(test_path)


# Test with excessively long log lines
@pytest.mark.asyncio
async def test_long_log_lines():
    long_log_path = f"{test_files_path}long_logs.log"
    with open(long_log_path, "w") as invalid_file:
        invalid_file.write("x" * 500 + "\n")

    test_path: set = set()
    test_path.add(long_log_path)
    await server.import_logs(test_path)