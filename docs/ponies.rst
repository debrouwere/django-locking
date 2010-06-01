=======
Roadmap
=======

Things that are planned
-----------------------

* hard locks (see :doc:`design`)
* manual overrides by admins
* enhance the warning dialog users see five minutes prior to expiry, to allow users to renew their lock
* make it so that locks do not trigger the ``auto_now`` or ``auto_now_add`` behavior of DateFields and DateTimeFields

Someday/maybe
-------------

* minimize dependence on javascript for soft locks, by using a middleware and Django's 1.2 ``read_only_fields``. ``django-locking`` won't be degrade entirely gracefully, but we do want to make sure it doesn't degrade quite so *ungracefully* as it does now.
* give end-developers a choice whether they want the LockableModel fields on the model itself (cleaner) or added with a OneToOneField instead (less hassle migrating if you're not using South__)
* userless locking (might be interesting if you want to lock stuff that a process is doing number crunching on, or something similar)

.. __: http://south.aeracode.org/