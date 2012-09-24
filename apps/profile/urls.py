from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'feed/$', views.feed),
    url(r'timeline/$', views.timeline),
    url(r'settings/$', views.settings),
    url(r'filter/add/$', views.filter_add),
    url(r'filter/remove/$', views.filter_remove),
    url(r'profile/$', views.profile),
    url(r'profile/reset_picture/$', views.reset_picture),
    url(r'profile/(?P<username>\w+)/$', views.profile),
    url(r'profile/(?P<username>\w+)/related/$', views.related_users),
    url(r'profile/(?P<username>\w+)/image/$', views.profile_image),
)
