from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^notifications/$', views.notifications),
    url(r'^following/add/$', views.add_followings),
    url(r'^lovers/add/$', views.add_lovers),
)
