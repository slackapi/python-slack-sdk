import requests


class SlackRequest(object):

    @staticmethod
    def do(token, request="?", post_data=None, domain="slack.com"):
        if post_data is None:
            post_data = {}

        if "files" in post_data:
            temp = dict(element:post_data[element] for element in post_data if not "files" in element)
            return requests.post(
            'https://{0}/api/{1}'.format(domain, request),
            data=dict(temp, token=token), files=post_data["files"]
            )
        else:
            return requests.post(
                'https://{0}/api/{1}'.format(domain, request),
                data=dict(post_data, token=token),
            )
