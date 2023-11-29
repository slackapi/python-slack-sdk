#!/bin/bash
# ./scripts/run_validation.sh

script_dir=`dirname $0`
cd ${script_dir}/..
pip install -U pip && \
  pip install -r requirements/testing.txt && \
  pip install -r requirements/optional.txt && \
  black slack_sdk/ slack/ tests/ integration_tests/ && \
  python setup.py codegen && \
  python setup.py validate
