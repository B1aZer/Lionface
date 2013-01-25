from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('schools.views',
    url(r'^$', 'home'),
    url(r'^add/$', 'add', name='schools-add'),
    url(r'^join/$', 'join', name='schools-join'),
    url(r'^leave/$', 'leave', name='schools-leave'),
)
