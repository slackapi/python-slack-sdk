#!/bin/bash
# ./scripts/install.sh
# Installs all project dependencies (testing, optional, and tools)

set -e

script_dir=$(dirname $0)
cd ${script_dir}/..

pip install -U pip

pip install -U -r requirements/testing.txt \
  -U -r requirements/optional.txt \
  -U -r requirements/tools.txt
