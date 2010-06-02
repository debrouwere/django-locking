import simplejson

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.contrib.auth.models import User

from locking import models, views, LOCK_TIMEOUT
from locking.tests.utils import TestCase
from locking.tests import models as testmodels

class AppTestCase(TestCase):
    fixtures = ['locking_scenario',]

    def setUp(self):
        self.story = testmodels.Story.objects.all()[0]
        users = User.objects.all()
        self.user, self.alt_user = users
    
    def test_decorator_user_may_change_model(self):
        raise NotImplementedError
    
    def test_decorator_is_lockable(self):
        raise NotImplementedError
    
    def test_hard_lock(self):
        # you can save a hard lock once (to initiate the lock)
        # but after that saving without first unlocking raises an error
        self.story.lock_for(self.user, hard_lock=True)
        self.assertEquals(self.story.lock_type, "hard")
        self.story.save()
        self.assertRaises(models.ObjectLockedError, self.story.save)
    
    def test_soft_lock(self):
        self.story.lock_for(self.user)
        self.story.save()
        self.assertEquals(self.story.lock_type, "soft")
        self.story.save() 
    
    def test_lock_for(self):
        self.story.lock_for(self.user)
        self.assertTrue(self.story.is_locked)
        self.story.save()
        self.assertTrue(self.story.is_locked)
  
    def test_lock_for_overwrite(self):
        # we shouldn't be able to overwrite an active lock by another user
        self.story.lock_for(self.alt_user)
        self.assertRaises(models.ObjectLockedError, self.story.lock_for, self.user)

    def test_unlock(self):
        self.story.lock_for(self.user)
        self.story.unlock()
        self.assertFalse(self.story.is_locked)
    
    def test_hard_unlock(self):
        self.story.lock_for(self.user, hard_lock=True)
        self.story.unlock_for(self.user)
        self.assertFalse(self.story.is_locked)
        self.story.unlock()

    def test_unlock_for_self(self):
        self.story.lock_for(self.user)
        self.story.unlock_for(self.user)
        self.assertFalse(self.story.is_locked)  

    def test_unlock_for_disallowed(self, hard_lock=False):
        # we shouldn't be able to disengage a lock that was put in place by another user
        self.story.lock_for(self.alt_user, hard_lock=hard_lock)
        self.assertRaises(models.ObjectLockedError, self.story.unlock_for, self.user)
    
    def test_hard_unlock_for_disallowed(self):
        self.test_unlock_for_disallowed(hard_lock=True)
    
    def test_lock_applies_to(self):
        self.story.lock_for(self.alt_user)
        applies = self.story.lock_applies_to(self.user)
        self.assertTrue(applies)
    
    def test_lock_doesnt_apply_to(self):
        self.story.lock_for(self.user)
        applies = self.story.lock_applies_to(self.user)
        self.assertFalse(applies)
    
    def test_is_locked_by(self):
        self.story.lock_for(self.user)
        self.assertEquals(self.story.locked_by, self.user)
    
    def test_is_unlocked(self):
        # this might seem like a silly test, but an object
        # should be unlocked unless it has actually been locked
        self.assertFalse(self.story.is_locked)
    
    def test_gather_lockable_models(self):
        from locking import utils
        from locking.tests import models
        lockable_models = utils.gather_lockable_models()
        self.assertTrue("story" in lockable_models["tests"])
        self.assertTrue("unlockable" not in lockable_models["tests"])

users = [
    {"username": "Stan", "password": "green pastures"},
    {"username": "Fred", "password": "pastures of green"},
    ]
    
# In case you didn't notice: these client tests are currently just stubs, 
# and are still very much on the todo-list.
class BrowserTestCase(object):
    apps = ('locking.tests', 'django.contrib.auth', 'django.contrib.admin', )

    def setUp(self):
        self.c = Client()
        self.c.post('/login/', **users[0])
        self.urls = {
            "lock": reverse(views.lock),
            "unlock": reverse(views.unlock),
            "is_locked": reverse(views.is_locked),
            "js_variables": reverse(views.js_variables),
            }
    
    def tearDown(self):
        pass

    def login(self):    
        self.c.post('/admin/login/', {})

    def logout(self):
        self.c.logout()
    
    def test_access_when_cannot_change_model(self):
        raise NotImplementedError
    
    def test_lock_when_allowed(self):

        self.c.get(self.urls['js_variables'])
        self.assertStatusCode(response)
    
    def test_lock_when_logged_out(self):
        self.logout()
        response = self.c.get(self.urls['lock'])
        self.assertStatusCode(response, 401)
    
    def test_lock_when_disallowed(self):
        self.assertStatusCode(response, 403)
    
    def test_unlock_when_allowed(self):
        self.assertStatusCode(response, 200)
    
    def test_unlock_when_disallowed(self):
        self.assertStatusCode(response, 403)
    
    def test_unlock_when_transpired(self):
        self.assertStatusCode(response, 403)
    
    def test_is_locked_when_applies(self):
        response = None
        self.assertStatusCode(response, 200)
        res = simplejson.loads(response)
        self.assertTrue(res['applies'])
        self.assertTrue(res['is_active'])
    
    def test_is_locked_when_self(self):
        response = None
        self.assertStatusCode(response, 200)
        res = simplejson.loads(response)
        self.assertFalse(res['applies'])
        self.assertTrue(res['is_active'])
    
    def test_js_variables(self):
        response = self.c.get(self.urls['js_variables'])
        self.assertStatusCode(response, 200)
        self.assertContains(response, LOCK_TIMEOUT)
    
    def test_admin_media(self):
        res = self.get('todo')
        self.assertContains(res, 'admin.locking.js')
    
    def test_admin_listedit_when_locked(self):
        # testen dat de listedit een locking-icoontje & de andere
        # boel weergeeft als een story op slot is
        res = None
        self.assertContains(res, 'locking/img/lock.png')
    
    def test_admin_listedit_when_locked_self(self):
        res = None
        self.assertContains(res, 'locking/img/page_edit.png')
    
    def test_admin_listedit_when_unlocked(self):
        res = None
        self.assertNotContains(res, 'locking/img')