#!/usr/bin/env bash

if ! [[ -x "$(command -v sphinx-build)" ]]; then
  pip install sphinx
fi

sphinx-build -E -c ./docs-src/_themes/slack/ -b html docs-src docs \
  && touch ./docs/.nojekyll \
  && cd docs/ \
  && mv _static/* assets/ \
  && find . -name '*.html' | xargs sed -i '' 's/_static/assets/'g \
  && cd -
