#!/bin/bash
# ./scripts/run_validation.sh

script_dir=`dirname $0`
cd ${script_dir}/..
pip install -U pip && \
  pip install -e ".[testing]" && \
  pip install -e ".[optional]" && \
  black slack_sdk/ slack/ tests/ && \
  python setup.py codegen && \
  python setup.py validate
