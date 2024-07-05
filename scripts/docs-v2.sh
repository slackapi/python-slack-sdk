#!/usr/bin/env bash

script_dir=`dirname $0`
cd ${script_dir}/..

sphinx-build -E -c ./docs-src-v2/_themes/slack/ -b html docs-src-v2 docs-v2 \
  && touch ./docs-v2/.nojekyll \
  && cd docs-v2/ \
  && mv _static/* assets/ \
  && find . -name '*.html' | xargs sed -i '' 's/_static/assets/'g \
  && cd -
