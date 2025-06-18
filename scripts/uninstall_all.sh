#!/bin/bash

# remove slack-sdk without a version specifier so that local builds are cleaned up
pip uninstall -y slack-sdk
# collect all installed packages
PACKAGES=$(pip freeze | grep -v "^-e" | sed 's/@.*//' | sed 's/\=\=.*//')
# uninstall packages without exiting on a failure 
for package in $PACKAGES; do
  pip uninstall -y $package
done
