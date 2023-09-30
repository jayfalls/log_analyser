#!/bin/bash

# Read the debug_mode file and extract the values of debug and test
debug=$(grep 'debug' debug_mode | cut -d'=' -f2 | tr -d ' ')
test=$(grep 'test' debug_mode | cut -d'=' -f2 | tr -d ' ')

# Create a virtual environment
python -m venv .env
source .env/bin/activate

# Install requirements
pip install -r requirements.txt

# Change directory to backend
cd backend

# Run python backend.py with or without -test parameter based on debug and test values
if [ "$debug" = "1" ] && [ "$test" = "1" ]; then
    python backend.py -test
else
    python backend.py
fi