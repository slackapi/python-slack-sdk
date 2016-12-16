from setuptools import setup

setup(name='slackclient',
      version='1.0.4',
      description='Python client for Slack.com',
      url='http://github.com/slackapi/python-slackclient',
      author='Ryan Huber',
      author_email='ryan@slack-corp.com',
      license='MIT',
      packages=['slackclient'],
      install_requires=[
        'websocket-client',
        'requests',
        'six',
      ],
      zip_safe=False)
