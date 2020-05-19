# ------------------
# Only for running this script here
import logging
import sys
from os.path import dirname

sys.path.insert(1, f"{dirname(__file__)}/../../..")
logging.basicConfig(level=logging.DEBUG)
# ------------------

# ---------------------
# Flask App
# ---------------------

import os

# pip install flask
from flask import Flask, make_response, request

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route("/slack/oauth/callback", methods=["GET"])
def endpoint():
    code = request.args.get("code")
    try:
        from slack import WebClient
        from slack.errors import SlackApiError
        client = WebClient(token="")
        client_id = os.environ["SLACK_CLIENT_ID"]
        client_secret = os.environ["SLACK_CLIENT_SECRET"]
        response = client.oauth_v2_access(client_id=client_id, client_secret=client_secret, code=code)
        result = response.get("error", "success!")
        return str(result)
    except SlackApiError as e:
        return make_response(str(e), 400)


if __name__ == "__main__":
    # export SLACK_CLIENT_ID=111.222
    # export SLACK_CLIENT_SECRET=
    # FLASK_ENV=development python integration_tests/samples/issues/issue_690.py
    app.run(debug=True, host="localhost", port=3000)
