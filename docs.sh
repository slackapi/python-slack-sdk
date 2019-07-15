#!/usr/bin/env bash

sphinx-build -c ./docs-src/_themes/slack/ -b html docs-src docs && touch ./docs/.nojekyll