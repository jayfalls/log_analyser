#!/bin/bash

# Read the debug_mode file and extract the values of debug and test
debug=$(grep 'debug' settings | cut -d'=' -f2 | tr -d ' ')
test=$(grep 'test' settings | cut -d'=' -f2 | tr -d ' ')

# Create a virtual environment
python3 -m venv .env
source .env/bin/activate

# Install requirements
pip3 install -r requirements.txt

# Run python backend.py with or without -test parameter based on debug and test values
run_commands=""
if [ "$debug" = "1" ]; then
    run_commands+="-debug"
    if [ "$test" = "1" ]; then
        run_commands+=" -test"
    fi
fi

cd app
python log_analyser.py "$run_commands"
