#!/bin/bash
# Generate API documents from the latest source code

script_dir=$(dirname "$0")
cd "${script_dir}"/.. || exit

pip install -U -r requirements/documentation.txt
pip install -U -r requirements/optional.txt

rm -rf docs/reference

pdoc slack_sdk --html -o docs/reference
cp -R docs/reference/slack_sdk/* docs/reference/
rm -rf docs/reference/slack_sdk

if [[ -z "${CI:-}" ]]; then
    open docs/reference/index.html
fi
