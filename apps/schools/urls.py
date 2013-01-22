from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('schools.views',
    url(r'^$', 'home'),
    url(r'^add/$', 'add', name='schools-add'),
)
