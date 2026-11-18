#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
echo '=== Build ==='
python3 --version
python3 -m py_compile app.py
echo '=== Test ==='
python3 -m unittest test_app.py -v
echo '=== Deploy ==='
mkdir -p deployment
cp app.py deployment/app.py
python3 deployment/app.py
echo 'Pipeline completed successfully'
