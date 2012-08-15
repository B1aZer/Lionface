from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'feed/$', views.feed),
    url(r'feed/(?P<user_id>\d+)/$', views.feed),
    url(r'save/$', views.save)
)