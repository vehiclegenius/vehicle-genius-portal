#!/usr/bin/env bash

# Exit on first error
set -e

. .pyenv/bin/activate
python3 -m pip install -r requirements.txt
