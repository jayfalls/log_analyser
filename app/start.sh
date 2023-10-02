#!/bin/bash

# Read the debug_mode file and extract the values of debug and test
debug=$(grep 'debug' settings | cut -d'=' -f2 | tr -d ' ')
test=$(grep 'test' settings | cut -d'=' -f2 | tr -d ' ')

# Create a virtual environment
python -m venv .env
source .env/bin/activate

# Install requirements
pip install -r requirements.txt
npm install bun --omit=dev

## NPM/BUN
export PATH="/Users/owner/.bun/bin:$PATH"
source PATH

# Change directory to backend
cd server

# Run python backend.py with or without -test parameter based on debug and test values
run_commands=""
if [ "$debug" = "1" ]; then
    run_commands+="-debug"
    if [ "$test" = "1" ]; then
        run_commands+=" -test"
    fi
fi

python server.py "$run_commands"