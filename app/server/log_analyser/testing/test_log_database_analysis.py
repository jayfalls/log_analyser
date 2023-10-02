import asyncio
import os
import pytest
import server


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

def test_analyse_logs_no_logs():
    with pytest.raises(Exception):
        server.analyse_logs()

def test_analyse_logs_invalid_filters():
    with pytest.raises(Exception):
        server.analyse_logs(filters=("invalid",))

def test_analyse_logs_empty_filters():
    results = server.analyse_logs(filters=())
    assert results == ()

def test_analyse_logs_invalid_log_ids():
    results = server.analyse_logs(filters=({"invalid"},)) 
    assert results == ()

def test_analyse_logs_nonexistent_log_ids():
    results = server.analyse_logs(filters=({"999"},))
    assert results == ()

def test_analyse_logs_valid_log_ids():
    results = server.analyse_logs(filters=({"123","456"},))
    assert len(results) == 2

def test_analyse_logs_invalid_date_range():
    with pytest.raises(ValueError):
        server.analyse_logs(filters=({"123"}, "invalid"))

def test_analyse_logs_valid_filters():
    results = server.analyse_logs(filters=({"123"}, ("2023-01-01", "2023-01-02")))
    assert len(results) == 1

def test_analyse_logs_multiple_filters():
    results = server.analyse_logs(filters=({"123"}, ("2023-01-01", "2023-01-02"), ("12:00", "13:00")))
    assert len(results) == 1