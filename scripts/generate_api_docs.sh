#!/bin/bash
# Generate API documents from the latest source code

script_dir=`dirname $0`
cd ${script_dir}/..

pip install -U -r requirements/documentation.txt
pip install -U -r requirements/optional.txt
rm -rf docs/static/api-docs
pdoc slack_sdk --html -o docs/static/api-docs
open docs/static/api-docs/slack_sdk/index.html
