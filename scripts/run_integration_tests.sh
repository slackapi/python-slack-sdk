#!/bin/bash
# Run all the tests or a single test
# all: ./scripts/run_integration_tests.sh
# single: ./scripts/run_integration_tests.sh integration_tests/web/test_async_web_client.py

set -e

script_dir=`dirname $0`
cd ${script_dir}/..

pip install -U pip
pip install -r requirements/testing.txt \
  -r requirements/optional.txt

echo "Generating code ..." && python scripts/codegen.py --path .
echo "Running black (code formatter) ..." && black slack_sdk/

test_target="${1:-tests/integration_tests/}"
PYTHONPATH=$PWD:$PYTHONPATH pytest $test_target
