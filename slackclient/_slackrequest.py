import requests


class SlackRequest(object):

    @staticmethod
    def do(token, request="?", post_data=None, domain="slack.com"):
        post_data = post_data or {}
        return requests.post(
            'https://{0}/api/{1}'.format(domain, request),
            data=dict(post_data, token=token),
        )
