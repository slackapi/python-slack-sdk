#!/bin/bash

pip uninstall -y slack-sdk && \
  pip freeze | grep -v "^-e" | xargs pip uninstall -y
