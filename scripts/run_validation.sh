#!/bin/bash
# all: ./scripts/run_validation.sh
# single: ./scripts/run_validation.sh tests/slack_sdk_async/web/test_web_client_coverage.py

set -e

script_dir=`dirname $0`
cd ${script_dir}/..

# keep in sync with LATEST_SUPPORTED_PY in .github/workflows/ci-build.yml
LATEST_SUPPORTED_PY="3.14"
current_py=$(python --version | sed -E 's/Python ([0-9]+\.[0-9]+).*/\1/')

./scripts/install.sh

echo "Generating code ..." && python scripts/codegen.py --path .
echo "Running black (code formatter) ..." && ./scripts/format.sh --no-install

echo "Running linting checks ..." && ./scripts/lint.sh --no-install

echo "Running tests with coverage reporting ..."
test_target="${1:-tests/}"
PYTHONPATH=$PWD:$PYTHONPATH pytest --cov-report=xml --cov=slack_sdk/ $test_target

# Run mypy type checking only on the latest supported Python version
if [[ "$current_py" == "$LATEST_SUPPORTED_PY" ]]; then
    echo "Running mypy type checking ..." && ./scripts/run_mypy.sh --no-install
fi
