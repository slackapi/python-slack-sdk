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

tests_require = ["pytest>=5,<6", "pytest-cov>=2,<3", "codecov>=2,<3", "flake8>=3,<4", "black", "psutil"]

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []


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
            self.status(s + "\n" + " ".join(command))
            subprocess.check_call(command)
        except subprocess.CalledProcessError as error:
            sys.exit(error.returncode)


class UploadCommand(BaseCommand):
    """Support setup.py upload. Thanks @kennethreitz!"""

    description = "Build and publish the package."

    def run(self):
        self._run(
            "Installing upload dependencies…",
            [sys.executable, "-m", "pip", "install", "wheel"],
        )
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self._run(
            "Building Source and Wheel (universal) distribution…",
            [sys.executable, "setup.py", "sdist", "bdist_wheel", "--universal"],
        )

        self._run(
            "Installing Twine dependency…",
            [sys.executable, "-m", "pip", "install", "twine"],
        )

        self._run(
            "Uploading the package to PyPI via Twine…",
            [sys.executable, "-m", "twine", "upload", "dist/*"],
        )

        self._run("Creating git tags…", ["git", "tag", f"v{__version__}"])
        self._run("Pushing git tags…", ["git", "push", "--tags"])


class ValidateCommand(BaseCommand):
    """Support setup.py validate."""

    description = "Run Python static code analyzer (flake8), formatter (black) and unit tests (pytest)."

    user_options = [
        ('unit-test-target=', 'i', 'tests/{unit-test-target}'),
        ('utt=', 'i', 'tests/{utt}'),
        ('test-target=', 'i', 'tests/{test-target}')
    ]

    def initialize_options(self):
        self.unit_test_target = ""
        self.utt = ""
        self.test_target = ""

    def run(self):
        self._run(
            "Installing test dependencies…",
            [sys.executable, "-m", "pip", "install"] + tests_require,
        )
        self._run("Running black…", [sys.executable, "-m", "black", f"{here}/slack"])
        self._run("Running flake8…", [sys.executable, "-m", "flake8", f"{here}/slack"])

        target = (self.utt or self.unit_test_target or self.test_target).replace("tests/", "")
        self._run(
            "Running pytest…",
            [
                sys.executable,
                "-m",
                "pytest",
                "--cov-report=xml",
                f"--cov={here}/slack",
                f"tests/{target}",
            ],
        )


class RunAllTestsCommand(ValidateCommand):
    """Support setup.py integration_test."""

    description = ValidateCommand.description + "\nRun integration tests (pytest)."

    user_options = [
        ('unit-test-target=', 'i', 'tests/{unit-test-target}'),
        ('utt=', 'i', 'tests/{utt}'),
        ('integration-test-target=', 'i', 'integration_tests/{integration-test-target}'),
        ('itt=', 'i', 'integration_tests/{itt}'),
        ('test-target=', 'i', 'integration_tests/{test-target}')
    ]

    def initialize_options(self):
        self.unit_test_target = ""
        self.utt = ""
        self.integration_test_target = ""
        self.itt = ""
        self.test_target = ""

    def run(self):
        ValidateCommand.run(self)
        target = (self.itt or self.integration_test_target or self.test_target).replace("integration_tests/", "")
        self._run(
            "Running pytest…",
            [
                sys.executable,
                "-m",
                "pytest",
                "--cov-report=xml",
                f"--cov={here}/slack",
                f"integration_tests/{target}",
            ],
        )


setup(
    name="slackclient",
    version=__version__,
    description="Slack API clients for Web API and RTM API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slackapi/python-slackclient",
    author="Slack Technologies, Inc.",
    author_email="opensource@slack.com",
    python_requires=">=3.6.0",
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Chat",
        "Topic :: System :: Networking",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="slack slack-web slack-rtm chat chatbots bots chatops",
    packages=find_packages(
        exclude=["docs", "docs-src", "integration_tests", "tests", "tests.*", "tutorial"]
    ),
    install_requires=["aiohttp>3.5.2,<4.0.0"],
    extras_require={"optional": ["aiodns>1.0"]},
    setup_requires=pytest_runner,
    test_suite="tests",
    tests_require=tests_require,
    cmdclass={
        "upload": UploadCommand,
        "validate": ValidateCommand,
        "run_all_tests": RunAllTestsCommand
    },
)
