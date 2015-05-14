from django.conf.urls import patterns, include, url
from django.contrib import admin
import couchsync

urlpatterns = patterns('',
    url(r'^couchsync/', include('couchsync.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
