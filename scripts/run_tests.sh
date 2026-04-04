#!/bin/bash
# Run all the tests or a single test
# all: ./scripts/run_tests.sh
# single: ./scripts/run_tests.sh tests/slack_sdk_async/web/test_web_client_coverage.py

set -e

script_dir=`dirname $0`
cd ${script_dir}/..

test_target="${1:-tests/}"

echo "Generating code ..." && python scripts/codegen.py --path .
echo "Running black (code formatter) ..." && ./scripts/format.sh --no-install

echo "Running tests ..."
PYTHONPATH=$PWD:$PYTHONPATH pytest $test_target
