# -*- coding: utf-8 -*-
import os
import subprocess
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

tests_require = ["pytest", "pytest-cov", "codecov", "flake8", "black"]


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

    def _run(self, s, command):
        try:
            self.status(s)
            subprocess.check_call(command)
        except subprocess.CalledProcessError as error:
            sys.exit(error.returncode)


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


class ValidateCommand(BaseCommand):
    """Support setup.py lint."""

    description = "Run Python static code analyzer (flake8), formatter (black) and unittests (pytest)."

    def run(self):
        self._run(
            "Installing test dependencies…",
            [sys.executable, "-m", "pip", "install"] + tests_require,
        )
        self._run(
            "Running black…", [sys.executable, "-m", "black", "{0}/slack".format(here)]
        )
        self._run(
            "Running flake8…",
            [sys.executable, "-m", "flake8", "{0}/slack".format(here)],
        )
        self._run(
            "Running pytest…",
            [
                sys.executable,
                "-m",
                "pytest",
                "-p",
                "pytest_cov",
                "--cov-report=",
                "--cov=slack",
                "tests/",
            ],
        )


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
    setup_requires=["pytest-runner"],
    test_suite="tests",
    tests_require=tests_require,
    cmdclass={"upload": UploadCommand, "validate": ValidateCommand},
)
