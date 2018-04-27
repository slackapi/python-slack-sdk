# Warning can be removed once we bump semver
import warnings
warnings.warn(
'Exceptions: SlackConnectionError and SlackLoginError have been moved '
'to exceptions imports from server are no longer supported and will be removed')

class SlackClientError(Exception):
    """
    Base exception for all errors raised by the SlackClient library
    """
    def __init__(self, msg=None):
        if msg is None:
            # default error message
            msg = "An error occurred in the SlackClient library"
        super(SlackClientError, self).__init__(msg)


class ParseResponseError(SlackClientError, ValueError):
    """
    Error raised when responses to Web API methods cannot be parsed as valid JSON
    """
    def __init__(self, response_body, original_exception):
        super(ParseResponseError, self).__init__(
            "Slack API response body could not be parsed: {0}. Original exception: {1}".format(
                response_body, original_exception
            )
        )
        self.response_body = response_body
        self.original_exception = original_exception


class SlackConnectionError(SlackClientError):
    def __init__(self, message='', reply=None):
        super(SlackConnectionError, self).__init__(message)
        self.reply = reply


class SlackLoginError(SlackClientError):
    def __init__(self, message='', reply=None):
        super(SlackLoginError, self).__init__(message)
        self.reply = reply
