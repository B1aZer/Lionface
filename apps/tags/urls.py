from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'add/$', views.add_tag),
    url(r'rem/$', views.rem_tag),
    url(r'deact/$', views.deactivate),
    url(r'act/$', views.activate),
)
