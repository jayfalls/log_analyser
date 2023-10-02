import asyncio
from log_analyser import log_analyser
import pytest
import sys
from log_analyser.log_analyser import LogAnalyser


# VARIABLES
## References
log_analyser: LogAnalyser = None
## States
debug_mode: bool = False


# TOOL CREATION4
def create_log_analyser() -> None:
    global log_analyser
    log_analyser = LogAnalyser()
    log_analyser.debug_mode = debug_mode


# LOG ANALYSER
async def import_logs(log_paths: set) -> None:
    if log_analyser is None:
        create_log_analyser()
    await log_analyser.import_logs(log_paths) 

def analyse_logs(filters: tuple = ()) -> tuple:
    if log_analyser is None:
        create_log_analyser()
    return log_analyser.analyse(filters)


# DEBUGGING
async def log_analyser_debug() -> None:
    # DEBUG VARIABLES
    test_log_path1: str = "log_analyser/.test_files/API2023_09_24.log"
    test_log_path2: str = "log_analyser/.test_files/API2023_09_27.log"
    test_log_paths: set = set()
    #log_paths.add(test_log_path1)
    test_log_paths.add(test_log_path2)

    create_log_analyser()
    await import_logs(test_log_paths)
    print(analyse_logs())


# STARTUP
def initialize() -> None:
    if __name__ != "__main__":
        return
    # No arguments
    if len(sys.argv) == 1:
        return
    # Check if "-debug" flag is provided
    if "-debug" in sys.argv[1]:
        global debug_mode
        sys.argv[1] = sys.argv[1].replace("-debug", "")
        debug_mode = True
    # Check if the '-test' flag is provided
    if not "-test" in sys.argv[1]:
        asyncio.run(log_analyser_debug())
        return
    # Remove '-test' from the command-line arguments to prevent pytest from considering it as a test
    sys.argv[1] = sys.argv[1].replace(" -test", "")
    # Run pytest with the specified arguments
    pytest.main(["--junitxml=testing/test_results.xml"])

initialize()