from django.conf.urls.defaults import patterns, url
import views


urlpatterns = patterns('',
    url(r'^change_status/$', views.change_status),
)


