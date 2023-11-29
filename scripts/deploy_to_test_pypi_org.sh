#!/bin/bash

script_dir=`dirname $0`
cd ${script_dir}/..
rm -rf ./slack_sdk.egg-info

pip install -U pip && \
  pip install twine build && \
  rm -rf dist/ build/ slack_sdk.egg-info/ && \
  python -m build --sdist --wheel && \
  twine check dist/* && \
  twine upload --repository testpypi dist/*
