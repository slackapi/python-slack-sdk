import logging

logging.basicConfig(level=logging.DEBUG)

# ---------------------
# Flask App for Slack OAuth flow
# ---------------------

import os
import json
from slack_sdk.web import WebClient
from slack_sdk.signature import SignatureVerifier

logger = logging.getLogger(__name__)
signature_verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

# ---------------------
# Flask App for Slack events
# ---------------------

from concurrent.futures.thread import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)

# pip3 install flask
from flask import Flask, request, make_response

app = Flask(__name__)
app.debug = True


@app.route("/slack/events", methods=["POST"])
def slack_app():
    request_body = request.get_data()
    if not signature_verifier.is_valid_request(request_body, request.headers):
        return make_response("invalid request", 403)

    if request.headers["content-type"] == "application/json":
        # Events API
        body = json.loads(request_body)
        if body["event"]["type"] == "workflow_step_execute":
            step = body["event"]["workflow_step"]

            def handle_step():
                try:
                    client.workflows_stepCompleted(
                        workflow_step_execute_id=step["workflow_step_execute_id"],
                        outputs={
                            "taskName": step["inputs"]["taskName"]["value"],
                            "taskDescription": step["inputs"]["taskDescription"]["value"],
                            "taskAuthorEmail": step["inputs"]["taskAuthorEmail"]["value"],
                        },
                    )
                except Exception as err:
                    client.workflows_stepFailed(
                        workflow_step_execute_id=step["workflow_step_execute_id"],
                        error={
                            "message": f"Something went wrong! ({err})",
                        },
                    )

            executor.submit(handle_step)
        return make_response("", 200)

    elif "payload" in request.form:
        # Action / View Submission
        body = json.loads(request.form["payload"])

        if body["type"] == "workflow_step_edit":
            new_modal = client.views_open(
                trigger_id=body["trigger_id"],
                view={
                    "type": "workflow_step",
                    "callback_id": "copy_review_view",
                    "blocks": [
                        {
                            "type": "section",
                            "block_id": "intro-section",
                            "text": {
                                "type": "plain_text",
                                "text": "Create a task in one of the listed projects. The link to the task and other details will be available as variable data in later steps.",
                            },
                        },
                        {
                            "type": "input",
                            "block_id": "task_name_input",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "task_name",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Write a task name",
                                },
                            },
                            "label": {"type": "plain_text", "text": "Task name"},
                        },
                        {
                            "type": "input",
                            "block_id": "task_description_input",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "task_description",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Write a description for your task",
                                },
                            },
                            "label": {"type": "plain_text", "text": "Task description"},
                        },
                        {
                            "type": "input",
                            "block_id": "task_author_input",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "task_author",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Write a task name",
                                },
                            },
                            "label": {"type": "plain_text", "text": "Task author"},
                        },
                    ],
                },
            )
            return make_response("", 200)

        if body["type"] == "view_submission" and body["view"]["callback_id"] == "copy_review_view":
            state_values = body["view"]["state"]["values"]

            client.workflows_updateStep(
                workflow_step_edit_id=body["workflow_step"]["workflow_step_edit_id"],
                inputs={
                    "taskName": {
                        "value": state_values["task_name_input"]["task_name"]["value"],
                    },
                    "taskDescription": {
                        "value": state_values["task_description_input"]["task_description"]["value"],
                    },
                    "taskAuthorEmail": {
                        "value": state_values["task_author_input"]["task_author"]["value"],
                    },
                },
                outputs=[
                    {
                        "name": "taskName",
                        "type": "text",
                        "label": "Task Name",
                    },
                    {
                        "name": "taskDescription",
                        "type": "text",
                        "label": "Task Description",
                    },
                    {
                        "name": "taskAuthorEmail",
                        "type": "text",
                        "label": "Task Author Email",
                    },
                ],
            )
            return make_response("", 200)

    return make_response("", 404)


if __name__ == "__main__":
    # export SLACK_BOT_TOKEN=***
    # export SLACK_SIGNING_SECRET=***
    # export FLASK_ENV=development

    app.run("localhost", 3000)

    # python3 integration_tests/samples/workflows/steps_from_apps.py
    # ngrok http 3000
    # POST https://{yours}.ngrok.io/slack/events
