==============
The public API
==============

Some examples
-------------

.. highlight:: python

Let's import some models and fixtures to play around with.

    >>> from locking.tests.models import Story
    >>> from django.contrib.auth.models import User
    >>> user = User.objects.all()[0]
    >>> story = Story.objects.all()[0]

Let's lock a story.

    >>> story.lock_for(user)
    INFO:root:Attempting to initiate a lock for user `stdbrouw`
    INFO:root:Initiated a lock for `stdbrouw` at 2010-06-01 09:33:46.540376
    # We can access all kind of information about the lock
    >>> s.locked_at
    datetime.datetime(2010, 6, 1, 9, 38, 3, 101238)
    >>> s.locked_by
    <User: stdbrouw>
    >>> s.is_locked
    True
    >>> s.lock_seconds_remaining
    1767
    # Remember: a lock isn't actually active until we save it to the database!
    >>> s.save()
    
And we can unlock again. Although it's possible to force an unlock, it's better to unlock specifically for the user that locked the content in the first place -- that way django-locking can protest if the wrong user tries to unlock something.

    >>> s.unlock_for(user)
    INFO:root:Attempting to open up a lock on `Story object` by user `blub`
    INFO:root:Attempting to initiate a lock for user `False`
    INFO:root:Freed lock on `Story object`
    True
    >>> s.save()

.. __: http://github.com/stdbrouw

Methods and attributes
----------------------

... are not quite documented yet. Expect this soon, and `badger me`__ about it if it's taking too long.

.. .. automodule:: locking.models
   :show-inheritance:
   :members:
   :undoc-members: