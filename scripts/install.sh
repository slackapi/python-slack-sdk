#!/bin/bash
# ./scripts/install.sh
# Installs all project dependencies (testing, optional, and tools)

script_dir=$(dirname $0)
cd ${script_dir}/..

pip install -U pip

pip install -U -r requirements/testing.txt
pip install -U -r requirements/optional.txt
pip install -U -r requirements/tools.txt
