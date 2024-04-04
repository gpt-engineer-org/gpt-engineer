#!/bin/bash

# a) Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# b) Run all necessary parts of the codebase
# Running tests in parallel is not directly applicable here, but we run the tests
pytest tests/
