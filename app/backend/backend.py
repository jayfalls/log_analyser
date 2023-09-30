import asyncio
from log_analyser import log_analyser
import pytest
import sys


# VARIABLES
## Temp
test_log_path: str = "log_analyser/.test_files/API2023_09_27.txt"


# LOG ANALYSER
async def run_log_analyser() -> None:
    await log_analyser.run_log_analyser(test_log_path)


# MAIN EXECUTION
if __name__ == '__main__':
    # Check if the '-test' flag is provided
    if '-test' in sys.argv:
        # Remove '-test' from the command-line arguments to prevent pytest from considering it as a test
        sys.argv.remove('-test')
        # Run pytest with the specified arguments
        pytest.main(['--junitxml=testing/test_results.xml'])
    else:
        # Run the log analyser
        asyncio.run(run_log_analyser())
