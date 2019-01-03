==============================================
Frequently Asked Questions
==============================================

What even is |product_name| and why should I care?
**************************************************

|product_name| is a wrapper around commonly accessed parts of the Slack Platform. It provides basic mechanisms for
using the Slack Web API from within your Python app.

On the other hand, |product_name| does not provide access to the Events bot-building API, but
[this adapter](https://github.com/slackapi/python-slack-events-api) does.

OMG I found a bug!
******************

Well, poop. Take a deep breath, and then let us know on the `Issue Tracker`_. If you're feeling particularly ambitious,
why not submit a `pull request`_ with a bug fix?

Hey, there's a feature missing!
*******************************

There's always something more that could be added! You can let us know in the `Issue Tracker`_ to start a discussion
around the proposed feature, that's a good start. If you're feeling particularly ambitious, why not write the feature
yourself, and submit a `pull request`_! We love feedback and we love help and we don't bite. Much.

I'd like to contribute...but how?
*********************************

What an excellent question. First of all, please have a look at our general `contributing guidelines`_. We'll wait for
you here.

All done? Great! While we're super excited to incorporate your new feature into |product_name|, there are a
couple of things we want to make sure you've given thought to.

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

This project's documentation is generated with `Sphinx <http://www.sphinx-doc.org>`_. If you are editing one of the many
reStructuredText files in the ``docs-src`` folder, you'll need to rebuild the documentation. It is recommended to run
the following steps inside a ``virtualenv`` environment.

.. code-block:: bash

  tox -e docs


Do be sure to add the ``docs`` folder and its contents to your pull request!


.. include:: metadata.rst
