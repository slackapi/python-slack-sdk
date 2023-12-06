#!/bin/bash
# Run all the tests or a single test
# all: ./scripts/run_unit_tests.sh
# single: ./scripts/run_unit_tests.sh tests/slack_sdk_async/web/test_web_client_coverage.py

set -e

script_dir=`dirname $0`
cd ${script_dir}/..

pip install -U pip
pip install -r requirements/testing.txt \
  -r requirements/optional.txt

python setup.py codegen

test_target="${1:-tests/}"
python setup.py unit_tests --test-target $test_target
