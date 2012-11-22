from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^notifications/$', views.notifications),
)
