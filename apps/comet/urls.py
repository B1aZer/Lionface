from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'messages/$', views.messages_check),
    url(r'notifications/$', views.notifiactions_check),
    url(r'permissions/$', views.permissions_check),
    url(r'new_posts/$', views.feed_posts),
)

