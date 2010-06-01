Developers' documentation
=========================

The public API
--------------

``django-locking`` has a concise API, revolving around the ``LockableModel``. You can read more about how to interact with this API in :doc:`api`.

Running the test suite
----------------------

If you want to run the test suite to ``django-locking``, just, eh, wait 'till I've had a chance to write this part of the documentation.

Building the documentation
--------------------------

Building the documentation can be done by simply cd'ing to the `/docs` directory and executing `make build html`. The documentation for Sphinx (the tool used to build the documentation) can be found here__, and a reStructured Text primer, which explains the markup language can be found here__.

.. __: http://sphinx.pocoo.org/index.html

.. __: http://sphinx.pocoo.org/rest.html

Help out
--------

If you'd like to help out with further development: fork away!

Design and other resources
--------------------------

You can learn a bit more about the rationale behind how ``django-locking`` works over at :doc:`design`.

You might also want to check out these web pages and see what kind of locking solutions are already out there: 

* http://www.reddit.com/r/django/comments/c8ts2/edit_locking_in_the_admin_anyone_ever_done_this/
* http://stackoverflow.com/questions/698950/what-is-the-simplest-way-to-lock-an-object-in-django
* http://djangosnippets.org/tags/lock/