from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^ajax/admin/', include('locking.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'', include('staticfiles.urls')),
)