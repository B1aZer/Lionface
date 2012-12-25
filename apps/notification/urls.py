from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'hide/(?P<notf_id>\d+)/$', views.hide_notification),
    url(r'$', views.notifications),
)
