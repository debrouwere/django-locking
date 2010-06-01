=====================
Design considerations
=====================

Pessimistic versus optimistic locking
-------------------------------------

Essentially, optimistic concurrency control will either give the user a warning or throw an exception whenever they try to overwrite a piece of content that has been updated since they last opened it for editing. Pessimistic concurrency control will actually lock the content for one specific user, so that nobody else can edit the content while he or she is working on it.

An optimistic system is easier to implement, but has the disadvantage of only preventing *overwrites*, not the actual concurrent editing -- which can be a pretty frustrating experience and a time waster for editors. Actual locking, that is, pessimistic concurrency control, can be a bit tricky to implement. Locks can often stay closed indefinitely or longer than expected because 

* a user's browser crashes before he navigates away from the page
* when a user leaves an edit screen open in a neglected tab
* the user navigates to another website without first saving

Any good locking system thus should be able to **unlock** the page even if the user navigates away from the website, but also has to implement **lock expiry** to handle the aforementioned edge cases. ``django-locking`` does both. In addition, it warns users when their lock is about to expire, so they can easily save their progress and edit the content again to initiate a new lock.

A short overview of different locking implementations
-----------------------------------------------------

Soft locks make sure to avoid concurrent edits in the Django admin interface, and also provide an interface by which you can check programatically if a piece of content is currently locked and act accordingly. However, a soft locking mechanism doesn't actually raise any exception when trying to save locked content, it only stops the save from occuring in the front-end of the website.

While soft locking may seem a little weird, it actually has a bunch of benefits. E.g. if you operate a pub review website that allows users to update the pricing of beer at different establishments, you may want to prevent an editor from updating a pub review when somebody else is updating the page, but may nevertheless still want to allow visitors to the site to update the price of a pint of beer, even though ``beer_price`` is an attribute on the same ``PubReview`` model.

However, sometimes, your application really does need to prevent the ``Model.save`` method from executing, and throw an exception when anybody except the person who initiated the lock tries to save. We'll call this **hard locking** In some cases, namely if other non-Django applications interface directly with your database, you might even want **database-level row locking**.

``django-locking`` currently does not support hard locks or database-level locks. Hard locks will be implemented soon (they're trivial to add). Database-level row locking might be added in the future, but is more difficult to get right, as the app has to ascertain that your database supports it. E.g. on MySQL ``InnoDB`` tables do, but ``MyISAM`` tables don't; sqlite has no row-level locking whatsoever but PostgreSQL does.