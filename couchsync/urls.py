from django.conf.urls import patterns, include, url
from .views import *

urlpatterns = patterns('',
    url(r'_changes$', ChangesFeedView.as_view(), name='changes'),
    url(r'_bulk_docs$', BulkDocsView.as_view(), name='bulk_docs'),
    url(r'_all_docs$', AllDocsView.as_view(), name='all_docs'),
    url(r'_revs_diff$', RevisionDiffView.as_view(), name='revs_diff'),
    url(r'(?P<docid>[^/]+)', SingleDocView.as_view(), name='singledoc'),
    url(r'', DatabaseInfoView.as_view(), name='database_info'),
)
