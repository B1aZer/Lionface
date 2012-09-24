from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'page/$', views.page),
    url(r'^$', views.main),
)

