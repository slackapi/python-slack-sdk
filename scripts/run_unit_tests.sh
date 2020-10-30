#!/bin/bash
# Run all the tests or a single test
# all: ./scripts/run_unit_tests.sh
# single: ./scripts/run_unit_tests.sh tests/slack_sdk_async/web/test_web_client_coverage.py

script_dir=`dirname $0`
cd ${script_dir}/..

test_target="$1"
python_version=`python --version | awk '{print $2}'`

if [[ $test_target != "" ]]
then
  black slack_sdk/ slack/ tests/ && \
    python setup.py codegen && \
    python setup.py unit_tests --test-target $1
else
  black slack_sdk/ slack/ tests/ && \
    python setup.py codegen && \
    python setup.py unit_tests
fi
