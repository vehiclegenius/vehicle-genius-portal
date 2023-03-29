#!/usr/bin/env bash

# TODO exit 1 if not in virtualenv

python3 -m pip freeze > requirements.txt
