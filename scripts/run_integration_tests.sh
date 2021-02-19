#!/bin/bash
# Run all the tests or a single test
# all: ./scripts/run_integration_tests.sh
# single: ./scripts/run_integration_tests.sh integration_tests/web/test_async_web_client.py

script_dir=`dirname $0`
cd ${script_dir}/..

test_target="$1"
python_version=`python --version | awk '{print $2}'`
pip install -e .

if [[ $test_target != "" ]]
then
  black slack_sdk/ slack/ tests/ && \
    python setup.py codegen && \
    python setup.py integration_tests --test-target $1
else
  black slack_sdk/ slack/ tests/ && \
    python setup.py codegen && \
    python setup.py integration_tests
fi
