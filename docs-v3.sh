#!/usr/bin/env bash

sphinx-build -E -c ./docs-src-v3/_themes/slack/ -b html docs-src-v3 docs-v3 && touch ./docs-v3/.nojekyll
