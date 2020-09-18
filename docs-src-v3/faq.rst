==============================================
FAQ
==============================================

Installation Issues
*********************************

We recommend using `virtualenv (venv) <https://docs.python.org/3/tutorial/venv.html>`_ to set up your Python runtime.

.. code-block:: bash

    # Create a dedicated virtual env for running your Python scripts
    python -m venv env

    # Run env\Scripts\activate on Windows OS
    source env/bin/activate

    # Install slack_sdk PyPI package
    pip install "slack_sdk>=3.0"

    # Set your token as an env variable (`set` command for Windows OS)
    export SLACK_BOT_TOKEN=xoxb-***

Then, verify the following code works on the Python REPL (you can start it by just ``python``).

.. code-block:: python

    import os
    import logging
    from slack_sdk import WebClient
    logging.basicConfig(level=logging.DEBUG)
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    res = client.api_test()


As ``slack`` package is deprecated, we recommend switching to ``slack_sdk`` package. That being said, the code you're working on may be still using the old package. If you encounter an error saying ``AttributeError: module 'slack' has no attribute 'WebClient'``, run ``pip list``. If you find both ``slack_sdk`` and ``slack`` in the output, try removing ``slack`` by ``pip uninstall slack`` and reinstalling ``slack_sdk``.


Bug Report
******************

That's great! Thank you. Let us know on the `Issue Tracker`_. If you're feeling particularly ambitious, why not submit a `pull request`_ with a bug fix?

Feature Requests
*******************************

There's always something more that could be added! You can let us know in the `Issue Tracker`_ to start a discussion around the proposed feature, that's a good start. If you're feeling particularly ambitious, why not write the feature yourself, and submit a `pull request`_! We love feedback and we love help and we don't bite. Much.

Contributions
*********************************

What an excellent question. First of all, please have a look at our general `contributing guidelines`_.

All done? Great! While we're super excited to incorporate your new feature, there are a couple of things we want to make sure you've given thought to.

- Please write unit tests for your new code. But don't **just** aim to increase the test coverage, rather, we expect you to have written **thoughtful** tests that ensure your new feature will continue to work as expected, and to help future contributors to ensure they don't break it!

- Please document your new feature. Think about **concrete use cases** for your feature, and add a section to the appropriate document, including a **complete** sample program that demonstrates your feature. Don't forget to update the changelog in ``changelog.rst``!

Including these two items with your pull request will totally make our day—and, more importantly, your future users' days!

On that note...

Documentation
*************************************

This project's documentation is generated with `Sphinx <http://www.sphinx-doc.org>`_. If you are editing one of the many reStructuredText files in the ``docs-src`` folder, you'll need to rebuild the documentation. It is recommended to run the following steps inside a ``virtualenv`` environment.

.. code-block:: bash

    ./docs-v3.sh

Do be sure to add the ``docs-v3`` folder and its contents to your pull request!

.. include:: metadata.rst
