#!/bin/bash


# Load modules
module load cray-python

set -x

# Create a virtual environment and install dependencies
python -m venv env
source env/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
