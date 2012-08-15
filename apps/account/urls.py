from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'signup/$', views.signup),
    url(r'login/$', views.login),
    url(r'logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'', include('django.contrib.auth.urls')),
    
    url(r'friend/add/$', views.friend_add),
    url(r'friend/accept/(?P<request_id>\d+)/$', views.friend_accept),
    url(r'friend/decline/(?P<request_id>\d+)/$', views.friend_decline),
)
