from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'feed/$', views.feed),
    url(r'timeline/(?P<post_num>\d+)/$', views.timeline),
    url(r'feed/(?P<user_id>\d+)/$', views.feed),
    url(r'save/$', views.save),
    url(r'del/(?P<post_id>\d+)/$', views.delete),
    url(r'show/$', views.show),
    url(r'share/(?P<post_id>\d+)/$', views.share)
)
