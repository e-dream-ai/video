#!/bin/bash

# Clone the submodule repository
git clone --recursive git@github.com:e-dream-ai/python-api.git python-api

# Install the submodule as a Python package
pip install -e python-api

# Run your worker script
python worker.py
