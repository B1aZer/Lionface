from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('schools.views',
    url(r'^$', 'home'),
    url(r'^detail/$', 'detail', name='schools-detail'),
    url(r'^add/$', 'add', name='schools-add'),
    url(r'^join/$', 'join', name='schools-join'),
    url(r'^leave/$', 'leave', name='schools-leave'),
    url(r'^search/$', 'search', name='schools-search'),

    url(r'^alum-in-year/$', 'alum_in_year', name='schools-alum-in-year'),
)
