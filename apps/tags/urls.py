from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'(?P<tag>\d+)/$', views.main),
)
