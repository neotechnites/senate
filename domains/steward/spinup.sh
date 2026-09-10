#!/bin/bash
# Steward Domain Head — spin up a session grounded in this pod's DB.
cd "$(dirname "$0")" && exec python3 spinup.py "$@"
