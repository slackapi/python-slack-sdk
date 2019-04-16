"""A Python module for managing any Slack client errors."""


class SlackClientError(Exception):
    """Base class for Client errors"""


class BotUserAccessError(SlackClientError):
    """Error raised when an 'xoxb-*' token is
    being used for a Slack API method that only accepts 'xoxp-*' tokens.
    """

    pass


class SlackRequestError(SlackClientError):
    """Error raised when there's a problem with the request that's being submitted.
    """

    pass


class SlackApiError(SlackClientError):
    """Error raised when Slack does not send the expected response."""

    def __init__(self, message, response):
        msg = ("{m}\nThe server responded with: {r}").format(m=message, r=response)
        self.response = response
        super(SlackApiError, self).__init__(msg)


class SlackClientNotConnectedError(SlackClientError):
    """Error raised when attempting to send messages over the websocket when the connection is closed."""

    pass
