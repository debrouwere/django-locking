# encoding: utf-8

from django.contrib import admin
from locking.tests import models
from locking.admin import LockableAdmin

class StoryAdmin(LockableAdmin):
    list_display = ('lock', 'content', )
    list_display_links = ('content', )

admin.site.register(models.Story, StoryAdmin)