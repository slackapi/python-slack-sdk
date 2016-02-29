from setuptools import setup

setup(name='slackclient',
      version='1.0.0',
      description='Python client for Slack.com',
      url='http://github.com/slackhq/python-slackclient',
      author='Ryan Huber',
      author_email='ryan@slack-corp.com',
      license='MIT',
      packages=['slackclient'],
      install_requires=[
        'websocket-client',
        'requests',
      ],
      zip_safe=False)
