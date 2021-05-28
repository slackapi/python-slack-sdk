#!/bin/bash
# ./scripts/run_validation.sh

script_dir=`dirname $0`
cd ${script_dir}/..
pip install "black==21.5b1"
black slack_sdk/ slack/ tests/ && \
  python setup.py codegen && \
  python setup.py validate
