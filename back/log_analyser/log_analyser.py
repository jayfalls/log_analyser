import asyncio
from tests import default_tests


# VARIABLES
# TEMP
test_log_path: str = ".test_files/API2023_09_27.txt"


# Loading Files
async def clean_log_file(log_path: str) -> str:
    valid_logs: str = ""
    try:
        with open(log_path, 'r') as log_file:
            loop = asyncio.get_event_loop()
            tasks = []
            for line in log_file:
                if "[REPORTING]" not in line:
                   valid_logs += line
            return valid_logs
    except FileNotFoundError:
        return "Log File does not exist"

def slow_clean(log_path: str) -> str:
    valid_logs: str = ""
    try:
        with open(log_path, 'r') as log_file:
            tasks = []
            for line in log_file:
                if "[REPORTING]" not in line:
                   valid_logs += line
            return valid_logs
    except FileNotFoundError:
        return "Log File does not exist"


# PROGRAM START
async def start() -> None:
    slow_time: str = default_tests.test_function_speed(slow_clean, test_log_path)
    fast_time: str = await default_tests.test_async_function_speed(clean_log_file, test_log_path)
    print(f"{slow_time}\n{fast_time}")
    logs: str = await clean_log_file(test_log_path)
    print(logs)

asyncio.run(start())