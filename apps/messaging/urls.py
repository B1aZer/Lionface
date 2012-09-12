from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'show/$', views.show),
    url(r'', views.messages),
)

