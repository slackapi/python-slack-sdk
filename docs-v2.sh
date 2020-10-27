#!/usr/bin/env bash

sphinx-build -E -c ./docs-src-v2/_themes/slack/ -b html docs-src-v2 docs-v2 && touch ./docs-v2/.nojekyll
