from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'feed/$', views.feed),
    url(r'timeline/$', views.timeline),
    url(r'profile/$', views.profile),
    url(r'profile/(?P<username>\w+)/$', views.profile),
)
