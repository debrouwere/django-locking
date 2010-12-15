from django.db import models
from locking import models as locking

class Story(locking.LockableModel):
    content = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'stories'

class Unlockable(models.Model):
    # this model serves to test that utils.gather_lockable_models
    # actually does what it's supposed to
    content = models.TextField(blank=True)