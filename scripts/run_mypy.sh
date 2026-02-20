#!/bin/bash
# ./scripts/run_mypy.sh

set -e

script_dir=$(dirname $0)
cd ${script_dir}/..

if [[ "$1" != "--no-install" ]]; then
    ./scripts/install.sh
fi

mypy --config-file pyproject.toml
