=========
Changelog
=========

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