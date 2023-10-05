import asyncio
import pytest
import sys
from program.log_analyser_interface import LogAnalyserInterface


# VARIABLES
## References
interface: LogAnalyserInterface = None
## States
debug_mode: bool = False


# TOOL CREATION / MODIFICATION
def create_interface() -> None:
    global interface
    interface = LogAnalyserInterface()
    interface.debug_mode = debug_mode

def update_filters(filters: tuple) -> None:
    global interface
    interface.set_filters(filters)


# LOG ANALYSIS
async def import_logs(log_paths: set) -> None:
    if interface is None:
        create_interface()
    await interface.import_logs(log_paths) 

def analyse_logs(filters: tuple = ()) -> tuple:
    if interface is None:
        create_interface()
    return interface.analyse()


# DEBUGGING
async def interface_debug() -> None:
    # DEBUG VARIABLES
    test_log_path1: str = "program/.test_files/API2023_09_24.log"
    test_log_path2: str = "program/.test_files/API2023_09_27.log"
    test_log_paths: set = set()
    #test_log_paths.add(test_log_path1)
    test_log_paths.add(test_log_path2)

    create_interface()
    await import_logs(test_log_paths)
    analyse_logs()


# INITIALISATION
def check_if_debug() -> bool:
    if not "-debug" in sys.argv[1]:
        return False
    global debug_mode
    sys.argv[1] = sys.argv[1].replace("-debug", "")
    debug_mode = True
    return True

def check_if_test() -> bool:
    if "-test" in sys.argv[1]:
        return True
    return False

def test() -> None:
    # Remove "-test" from the command-line arguments to prevent pytest from considering it as a test
    sys.argv[1] = sys.argv[1].replace(" -test", "")
    # Run pytest with the specified arguments
    pytest.main(["--junitxml=testing/test_results.xml"])

def initialize() -> None:
    if __name__ != "__main__":
        return
    if len(sys.argv) == 1: # No arguments
        return
    if not check_if_debug():
        return
    if not check_if_test():
        asyncio.run(interface_debug())
        return
    test()

initialize()