#!/bin/bash

pip uninstall -y slack-sdk && \
  pip freeze | grep -v "^-e" | sed 's/@.*//' | sed 's/\=\=.*//' | xargs pip uninstall -y
