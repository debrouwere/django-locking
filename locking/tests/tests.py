from datetime import datetime, timedelta
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
        self.alt_story, self.story = testmodels.Story.objects.all()
        users = User.objects.all()
        self.user, self.alt_user = users
    
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
    
    def test_lock_expiration(self):
        self.story.lock_for(self.user)
        self.assertTrue(self.story.is_locked)
        self.story._locked_at = datetime.today() - timedelta(minutes=LOCK_TIMEOUT+1)
        self.assertFalse(self.story.is_locked)
    
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

    def test_locking_bit_when_locking(self):
        # when we've locked something, we should set an administrative
        # bit so other developers can know a save will do a lock or 
        # unlock and respond to that information if they so wish.
        self.story.content = "Blah"
        self.assertEquals(self.story._state.locking, False)
        self.story.lock_for(self.user)
        self.assertEquals(self.story._state.locking, True)
        self.story.save()
        self.assertEquals(self.story._state.locking, False)        

    def test_locking_bit_when_unlocking(self):
        # when we've locked something, we should set an administrative
        # bit so other developers can know a save will do a lock or 
        # unlock and respond to that information if they so wish.
        self.story.content = "Blah"
        self.assertEquals(self.story._state.locking, False)
        self.story.lock_for(self.user)
        self.story.unlock_for(self.user)
        self.assertEquals(self.story._state.locking, True)        
        self.story.save()
        self.assertEquals(self.story._state.locking, False)  

    def test_unlocked_manager(self):
        self.story.lock_for(self.user)
        self.story.save()
        self.assertEquals(testmodels.Story.objects.count(), 2)
        self.assertEquals(testmodels.Story.unlocked.count(), 1)
        self.assertEquals(testmodels.Story.unlocked.get(pk=self.alt_story.pk).pk, 1)
        self.assertRaises(testmodels.Story.DoesNotExist, testmodels.Story.unlocked.get, pk=self.story.pk)
        self.assertNotEquals(testmodels.Story.unlocked.all()[0].pk, self.story.pk)

    def test_locked_manager(self):
        self.story.lock_for(self.user)
        self.story.save()
        self.assertEquals(testmodels.Story.objects.count(), 2)
        self.assertEquals(testmodels.Story.locked.count(), 1)
        self.assertEquals(testmodels.Story.locked.get(pk=self.story.pk).pk, 2)
        self.assertRaises(testmodels.Story.DoesNotExist, testmodels.Story.locked.get, pk=self.alt_story.pk)
        self.assertEquals(testmodels.Story.locked.all()[0].pk, self.story.pk)

    def test_managers(self):
        self.story.lock_for(self.user)
        self.story.save()
        locked = testmodels.Story.locked.all()
        unlocked = testmodels.Story.unlocked.all()
        self.assertEquals(locked.count(), 1)
        self.assertEquals(unlocked.count(), 1)
        self.assertTrue(len(set(locked).intersection(set(unlocked))) == 0)

users = [
    # Stan is a superuser
    {"username": "Stan", "password": "green pastures"},
    # Fred has pretty much no permissions whatsoever
    {"username": "Fred", "password": "pastures of green"},
    ]
    
class BrowserTestCase(TestCase):
    fixtures = ['locking_scenario',]
    apps = ('locking.tests', 'django.contrib.auth', 'django.contrib.admin', )
    # REFACTOR: 
    # urls = 'locking.tests.urls'

    def setUp(self):
        # some objects we might use directly, instead of via the client
        self.story = story = testmodels.Story.objects.all()[0]
        user_objs = User.objects.all()
        self.user, self.alt_user = user_objs
        # client setup
        self.c = Client()
        self.c.login(**users[0])
        story_args = [story._meta.app_label, story._meta.module_name, story.pk]
        # refactor: http://docs.djangoproject.com/en/dev/topics/testing/#urlconf-configuration
        # is probably a smarter way to go about this
        self.urls = {
            "change": reverse('admin:tests_story_change', args=[story.pk]),
            "changelist": reverse('admin:tests_story_changelist'),
            "lock": reverse(views.lock, args=story_args),
            "unlock": reverse(views.unlock, args=story_args),
            "is_locked": reverse(views.is_locked, args=story_args),
            "js_variables": reverse(views.js_variables),
            }
    
    def tearDown(self):
        pass

    # Some terminology: 
    # - 'disallowed' is when the locking system does not allow a certain operation
    # - 'unauthorized' is when Django does not permit a user to do something
    # - 'unauthenticated' is when a user is logged out of Django
      
    def test_lock_when_allowed(self):
        res = self.c.get(self.urls['lock'])        
        self.assertEquals(res.status_code, 200)
        # reload our test story
        story = testmodels.Story.objects.get(pk=self.story.id)
        self.assertTrue(story.is_locked)
        
    def test_lock_when_logged_out(self):
        self.c.logout()
        res = self.c.get(self.urls['lock'])
        self.assertEquals(res.status_code, 401)
    
    def test_lock_when_unauthorized(self):
        # when a user doesn't have permission to change the model
        # this tests the user_may_change_model decorator
        self.c.logout()
        self.c.login(**users[1])
        res = self.c.get(self.urls['lock'])        
        self.assertEquals(res.status_code, 401)
    
    def test_lock_when_does_not_apply(self):
        # don't make a resource available to lock models that don't 
        # have locking enabled -- this tests the is_lockable decorator
        obj = testmodels.Unlockable.objects.get(pk=1)
        args = [obj._meta.app_label, obj._meta.module_name, obj.pk]
        url = reverse(views.lock, args=args)
        res = self.c.get(url)        
        self.assertEquals(res.status_code, 404)              
    
    def test_lock_when_disallowed(self):
        self.story.lock_for(self.alt_user)
        self.story.save()
        res = self.c.get(self.urls['lock'])        
        self.assertEquals(res.status_code, 403)
    
    def test_unlock_when_allowed(self):
        self.story.lock_for(self.user)
        self.story.save()
        res = self.c.get(self.urls['unlock'])        
        self.assertEquals(res.status_code, 200)
        # reload our test story
        story = testmodels.Story.objects.get(pk=self.story.id)
        self.assertFalse(story.is_locked)
    
    def test_unlock_when_disallowed(self):
        self.story.lock_for(self.alt_user)
        self.story.save()
        res = self.c.get(self.urls['unlock'])        
        self.assertEquals(res.status_code, 403)

    def test_is_locked_when_applies(self):
        self.story.lock_for(self.alt_user)
        self.story.save()
        res = self.c.get(self.urls['is_locked'])
        res = simplejson.loads(res.content)
        self.assertTrue(res['applies'])
        self.assertTrue(res['is_active'])
    
    def test_is_locked_when_self(self):
        self.story.lock_for(self.user)
        self.story.save()
        res = self.c.get(self.urls['is_locked'])
        res = simplejson.loads(res.content)
        self.assertFalse(res['applies'])
        self.assertTrue(res['is_active'])

    def test_js_variables(self):
        res = self.c.get(self.urls['js_variables'])
        self.assertEquals(res.status_code, 200)
        self.assertContains(res, LOCK_TIMEOUT)
    
    def test_admin_media(self):
        res = self.c.get(self.urls['change'])
        self.assertContains(res, 'admin.locking.js')
    
    def test_admin_changelist_when_locked(self):
        self.story.lock_for(self.alt_user)
        self.story.save()
        res = self.c.get(self.urls['changelist'])
        self.assertContains(res, 'locking/img/lock.png')
    
    def test_admin_changelist_when_locked_self(self):
        self.test_lock_when_allowed()
        res = self.c.get(self.urls['changelist'])
        self.assertContains(res, 'locking/img/page_edit.png')
    
    def test_admin_changelist_when_unlocked(self):
        res = self.c.get(self.urls['changelist'])
        self.assertNotContains(res, 'locking/img')