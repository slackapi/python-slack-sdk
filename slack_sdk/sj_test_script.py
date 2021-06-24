import logging
import asyncio

from slack_sdk.webhook import WebhookClient

# from slack_sdk.webhook import AsyncWebhookClient

url = (
    "https://hooks.slack.com/services/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"
)
webhook = WebhookClient(url)

# way 1 with a simple text message and .send()
url = "<https://imgs.xkcd.com/comics/new_sports_system_2x.png>"
message_with_url = f"hello webhook world\n{url}"

# way 2 with a body and .send_dict()
text = message_with_url
dict = {"text": text, "unfurl_links": True, "unfurl_media": True}


async def main():
    response = await webhook.send(
        text=message_with_url, unfurl_media=True, unfurl_links=False
    )
    return response


if __name__ == "__main__":
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())
    response = asyncio.run(main())  # way 1
    # response = webhook.send_dict(dict)  # way 2
    log.debug(response.body)
    assert response.status_code == 200
    assert response.body == "ok"


# Example Urls

# These testing conditions are done so with
# the knowledge that repeated urls (w/in the
# same hour will not unfurl:

# Test Conditions 0
# Conditions: no additional args
# Expected:
#   - When text based link  is supplied <api.slack.com> -> no unfurl ✅
#   - When a text based link is supplied with same domain <api.slack.com|api.slack.com> -> no unfirl ✅
#   - When a text based link is supplied <https://github.com/slackapi/python-slack-sdk/blob/main/.github/maintainers_guide.md> -> no unfirl ✅
#   - When a text based link is supplied with different domain <https://slack.com/|Maintenance> -> unfirl 🔴

# Test Conditions 1
# Conditions: links = False, media = False
# Expected:
#   - When link is supplied -> No unfurl
#   - When media is supplied ->  No unfurl
# Actual:
#   - When link is supplied -> ❓
#   - When media is supplied -> ❓

# Test Conditions 2
# Conditions: links = True, media = True
# Expected:
#   - When link is supplied -> Unfurl
#   - When media is supplied ->  Unfurl
# Actual:
#   - When link is supplied -> ❓
#   - When media is supplied -> ❓

# Test Conditions 3
# Conditions: links = False, media = True
# Expected:
#   - When link is supplied -> No unfurl
#   - When media is supplied ->  Unfurl
# Actual:
#   - When link is supplied -> ❓
#   - When media is supplied -> ❓

# Test Conditions 4
# Conditions: links = True, media = False
# Expected:
#   - When link is supplied -> Unfurl
#   - When media is supplied ->  No unfurl
# Actual:
#   - When link is supplied -> ❓
#   - When media is supplied -> ❓
