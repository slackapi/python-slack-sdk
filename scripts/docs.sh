#!/usr/bin/env bash

script_dir=`dirname $0`
cd ${script_dir}/..

if ! [[ -x "$(command -v sphinx-build)" ]]; then
  pip install sphinx
fi

sphinx-build -E -c ./docs-src/_themes/slack/ -b html docs-src docs \
  && touch ./docs/.nojekyll \
  && cd docs/ \
  && mv _static/* assets/ \
  && find . -name '*.html'| grep -v api-docs | xargs sed -i '' 's/_static/assets/'g \
  && cd -
