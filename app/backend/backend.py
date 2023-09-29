import asyncio
from log_analyser import log_analyser


# VARIABLES
## Temp
test_log_path: str = "log_analyser/.test_files/API2023_09_27.txt"


# LOG ANALYSER
async def run_log_analyser() -> None:
    await log_analyser.run_log_analyser(test_log_path)

asyncio.run(run_log_analyser())
