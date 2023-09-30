import asyncio
from log_analyser import log_analyser
import pytest
import sys


# VARIABLES
## Temp
test_log_path: str = "log_analyser/.test_files/API2023_09_27.log"


# LOG ANALYSER
async def run_log_analyser() -> None:
    await log_analyser.run_log_analyser(test_log_path)


# STARTUP
def initialize() -> None:
    if __name__ != "__main__":
        return
    # Check if "-debug" flag is provided
    if "-debug" in sys.argv[1]:
        sys.argv[1] = sys.argv[1].replace("-debug", "")
        log_analyser.debug_mode = True
    # Check if the '-test' flag is provided
    if not "-test" in sys.argv[1]:
        asyncio.run(run_log_analyser())
        return
    # Remove '-test' from the command-line arguments to prevent pytest from considering it as a test
    sys.argv[1] = sys.argv[1].replace(" -test", "")
    # Run pytest with the specified arguments
    pytest.main(["--junitxml=testing/test_results.xml"])

initialize()