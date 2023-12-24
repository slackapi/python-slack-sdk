#!/bin/bash
# ./scripts/run_validation.sh

set -e

script_dir=`dirname $0`
cd ${script_dir}/..

pip install -U pip setuptools wheel
pip install -r requirements/testing.txt \
  -r requirements/optional.txt

python setup.py codegen
python setup.py validate
