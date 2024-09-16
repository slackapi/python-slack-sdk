#!/bin/bash
# ./scripts/run_mypy.sh

script_dir=$(dirname $0)
cd ${script_dir}/.. && \
  pip install .
  pip install -r requirements/testing.txt && \
  mypy --config-file pyproject.toml
