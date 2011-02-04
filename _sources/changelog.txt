=========
Changelog
=========

1.0 (pending)
-------------

V hard locks and soft locks (see :doc:`design`)
* improve the test coverage with web client tests
* more docstrings and more documentation in general
* i18n: Dutch translation
* manual overrides by admins (in the UI)
* enhance the warning dialog users see five minutes prior to expiry, to allow users to renew their lock
* make it so that locks do not trigger the ``auto_now`` or ``auto_now_add`` behavior of DateFields and DateTimeFields

0.2
---

* Initial open-source release
* Added packaging for PyPI
* Added a bunch of documentation, both for end-developers and to explain its underlying design
* Got rid of some assumptions and various little bits of hardcoding. E.g. urls are now constructed using Django's ``django.core.urlresolvers.reverse`` wherever possible.
* Static media serving using ``django-staticfiles``
* Added unit tests 

0.1
---

* Internal release