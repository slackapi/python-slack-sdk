==============================================
Frequently Asked Questions
==============================================

I found a bug!
******************

That's great! Thank you. Let us know on the `Issue Tracker`_. If you're feeling particularly ambitious, why not submit a `pull request`_ with a bug fix?

There's a feature missing!
*******************************

There's always something more that could be added! You can let us know in the `Issue Tracker <https://github.com/slackapi/python-slackclient/issues>`_ to start a discussion around the proposed feature, that's a good start. If you're feeling particularly ambitious, why not write the feature yourself, and submit a `pull request <https://github.com/slackapi/python-slackclient/pulls>`_! We love feedback and we love help and we don't bite. Much.

How do I contribute?
*********************************

What an excellent question. First of all, please have a look at our general `contributing guidelines <https://github.com/slackapi/python-slackclient/blob/master/.github/contributing.md>`_.

All done? Great! While we're super excited to incorporate your new feature, there are a couple of things we want to make sure you've given thought to.

- Please write unit tests for your new code. But don't **just** aim to increase the test coverage, rather, we expect you
  to have written **thoughtful** tests that ensure your new feature will continue to work as expected, and to help future
  contributors to ensure they don't break it!

- Please document your new feature. Think about **concrete use cases** for your feature, and add a section to the
  appropriate document, including a **complete** sample program that demonstrates your feature. Don't forget to update
  the changelog in ``changelog.rst``!

Including these two items with your pull request will totally make our day—and, more importantly, your future users' days!

On that note...

How do I compile the documentation?
***********************************

This project's documentation is generated with `Sphinx <http://www.sphinx-doc.org>`_. If you are editing one of the many reStructuredText files in the ``docs-src`` folder, you'll need to rebuild the documentation. It is recommended to run the following steps inside a ``virtualenv`` environment.

.. code-block:: bash

  tox -e docs

Do be sure to add the ``docs`` folder and its contents to your pull request!


.. include:: metadata.rst
