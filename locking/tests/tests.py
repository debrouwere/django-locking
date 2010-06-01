import simplejson

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.contrib.auth.models import User

from locking import models, views, LOCK_TIMEOUT
from locking.tests.utils import TestCase
from locking.tests.models import Story



class AppTests(TestCase):
    def setUp(self):
        self.story = Story.objects.all()[0]
        users = User.objects.all()
        self.user = users[0]
        self.alt_user = users[1]
    
    def tearDown(self):
        pass
        # flush & load fixtures opnieuw
    
    def test_decorator_user_may_change_model(self):
        raise NotImplementedError
    
    def test_decorator_is_lockable(self):
        raise NotImplementedError
    
    def test_lock_for(self):
        self.story.lock_for(self.user)
        self.assertTrue(self.story.is_locked)
        self.story.save()
        self.assertTrue(self.story.is_locked)
    
    def test_lock_for_overwrite(self):
        # we shouldn't be able to overwrite a lock by another user
        self.story.lock_for(self.alt_user)
        self.story.lock_for(self.user)
        self.assertTrue(self.locked_by, self.alt_user)
    
    def test_unlock_for_self(self):
        self.story.lock_for(self.user)
        unlocked = self.story.unlock_for(self.user)
        # assertException? of met een catch zodat we de exception vangen?
        self.assertTrue(unlocked)  
    
    def test_unlock_for_disallowed(self):
        self.story.lock_for(self.alt_user)
        unlocked = self.story.unlock_for(self.user)
        # assertException? of met een catch zodat we de exception vangen?
        self.assertFalse(unlocked)      
    
    def test_unlock(self):
        raise NotImplementedError
    
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
        self.assertFalse(self.story.is_locked)
    
    def test_unlock_upon_save(self):
        self.story.lock_for(self.user)
        self.story.save()
        self.assertFalse(self.story.is_locked)
    
    def test_gather_lockable_models(self):
        from locking import utils
        from locking.tests import models
        lockable_models = utils.gather_lockable_models()
        self.assertTrue(models.Story in lockable_models)
        self.assertTrue(models.Unlockable not in lockable_models)

class BrowserTests(TestCase):
    apps = ('locking.tests', 'django.contrib.auth', 'django.contrib.admin', )

    def login(self):
        self.c.post('/admin/login/', {})

    def logout(self):
        self.c.logout()

    def setUp(self):
        self.c = Client()
        self.c.post('/login/', {'name': 'fred', 'passwd': 'secret'})
        self.urls = {
            "lock": reverse(views.lock),
            "unlock": reverse(views.unlock),
            "is_locked": reverse(views.is_locked),
            "js_variables": reverse(views.js_variables),
            }
    
    def tearDown(self):
        pass
    
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