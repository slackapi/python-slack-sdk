import requests


class SlackRequest(object):
    def do(self, token, request="?", post_data={}, domain="slack.com"):
        return requests.post(
            'https://{0}/api/{1}'.format(domain, request),
            data=dict(post_data, token=token),
        )
