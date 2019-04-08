# -*- coding: utf-8 -*-
import os
import sys
from shutil import rmtree
from setuptools import setup, find_packages, Command
import codecs

__version__ = None
exec(open("slack/version.py").read())

here = os.path.abspath(os.path.dirname(__file__))

long_description = ""
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as readme:
    long_description = readme.read()


class BaseCommand(Command):
    """Base Command"""

    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class UploadCommand(BaseCommand):
    """Support setup.py upload. Thanks @kennethreitz!"""

    description = "Build and publish the package."

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(__version__))
        os.system("git push --tags")

        sys.exit()


class LintCommand(BaseCommand):
    """Support setup.py lint."""

    description = "Run Python static code analyzer (flake8) and formatter (black)."

    def run(self):
        self.status("Running black…")
        os.system("{0} -m black {1}/slack".format(sys.executable, here))

        self.status("Running flake8…")
        os.system("{0} -m flake8 {1}/slack".format(sys.executable, here))
        sys.exit()


setup(
    name="slackclient",
    version=__version__,
    description="Slack API clients for Web API and RTM API",
    long_description=long_description,
    url="https://github.com/slackapi/python-slackclient",
    author="Slack Technologies, Inc.",
    author_email="opensource@slack.com",
    python_requires=">=3.6.0",
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Chat",
        "Topic :: System :: Networking",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="slack slack-web slack-rtm chat chatbots bots chatops",
    packages=find_packages(exclude=["docs", "docs-src", "tests", "tests.*"]),
    install_requires=["websockets>6.0", "requests>2.20"],
    setup_requires=["pytest-runner", "flake8", "black"],
    test_suite="tests",
    tests_require=["pytest", "codecov"],
    cmdclass={"upload": UploadCommand, "lint": LintCommand},
)
