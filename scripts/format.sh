#!/bin/bash
# ./scripts/format.sh

script_dir=`dirname $0`
cd ${script_dir}/..

pip install -U pip
pip install -U -r requirements/tools.txt

black slack/ slack_sdk/ tests/ integration_tests/
