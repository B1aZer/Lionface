from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'feed/$', views.feed),
    url(r'timeline/$', views.timeline),
    url(r'profile/$', views.profile),
    url(r'settings/$', views.settings),
    url(r'messages/$', views.messages),
    url(r'filter/add/$', views.filter_add),
    url(r'filter/remove/$', views.filter_remove),
    url(r'profile/(?P<username>\w+)/$', views.profile),
)
