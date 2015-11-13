from setuptools import setup

setup(name='slackclient',
      version='0.16',
      description='Python client for Slack.com',
      url='http://github.com/slackhq/python-slackclient',
      author='Ryan Huber',
      author_email='ryan@slack-corp.com',
      license='MIT',
      packages=['slackclient'],
      install_requires=[
        'websocket-client',
        'future',
      ],
      zip_safe=False)
