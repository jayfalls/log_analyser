import asyncio
from log_analyser import log_analyser
import pytest
import sys


# STARTUP
def initialize() -> None:
    if __name__ != "__main__":
        return
    # No arguments
    if len(sys.argv) == 1:
        return
    # Check if "-debug" flag is provided
    if "-debug" in sys.argv[1]:
        sys.argv[1] = sys.argv[1].replace("-debug", "")
        log_analyser.debug_mode = True
    # Check if the '-test' flag is provided
    if not "-test" in sys.argv[1]:
        asyncio.run(log_analyser.load_test_logs())
        return
    # Remove '-test' from the command-line arguments to prevent pytest from considering it as a test
    sys.argv[1] = sys.argv[1].replace(" -test", "")
    # Run pytest with the specified arguments
    pytest.main(["--junitxml=testing/test_results.xml"])

initialize()