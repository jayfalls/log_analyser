import pytest
import sys
import tkinter
from program.log_analyser_interface import LogAnalyserInterface
from gui.gui import GUI


# VARIABLES
## References
interface: LogAnalyserInterface = None
gui: GUI
## States
debug_mode: bool = False


# CREATION / MODIFICATION
def create_interface() -> None:
    global interface
    interface = LogAnalyserInterface()
    interface.debug_mode = debug_mode

def create_gui() -> None:
    global gui
    gui = GUI(interface)

def update_filters(filters: tuple) -> None:
    global interface
    interface.set_filters(filters)

# PROGRAM
def start_program() -> None:
    create_interface()
    create_gui()


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
        start_program()
        return
    if not check_if_debug():
        return
    if not check_if_test():
        start_program()
        return
    test()

initialize()