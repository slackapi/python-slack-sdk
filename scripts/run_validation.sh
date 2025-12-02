#!/bin/bash
# all: ./scripts/run_validation.sh
# single: ./scripts/run_validation.sh tests/slack_sdk_async/web/test_web_client_coverage.py

set -e

script_dir=`dirname $0`
cd ${script_dir}/..

pip install -U -r requirements/testing.txt \
  -U -r requirements/optional.txt \
  -U -r requirements/tools.txt

echo "Generating code ..." && python scripts/codegen.py --path .
echo "Running black (code formatter) ..." && ./scripts/format.sh --no-install

echo "Running linting checks ..." && ./scripts/lint.sh --no-install

echo "Running tests with coverage reporting ..."
test_target="${1:-tests/}"
PYTHONPATH=$PWD:$PYTHONPATH pytest --cov-report=xml --cov=slack_sdk/ $test_target
