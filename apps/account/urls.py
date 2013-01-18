from django.conf.urls.defaults import patterns, include, url
from registration.views import activate
from django.core.urlresolvers import reverse
import views

urlpatterns = patterns('',
    url(r'^activate/(?P<activation_key>\w+)/$',
                           activate,
                           {
                               'backend': 'registration.backends.default.DefaultBackend',
                               'success_url':'/',
                           },
                           name='registration_activate'),

    url(r'pending_email_verification/$', views.pending, name='pending'),
    url(r'resend_activation/$', views.resend_activation),
    url(r'change_email/$', views.change_email),
    url(r'save_email/$', views.save_email),

    url(r'signup/$', views.signup, name='signup'),
    url(r'login/$', views.login),
    url(r'logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'', include('django.contrib.auth.urls')),
    #url(r'', include('registration.backends.default.urls')),

    url(r'friend/add/$', views.friend_add),
    url(r'friend/remove/$', views.friend_remove),
    url(r'friend/accept/(?P<request_id>\d+)/$', views.friend_accept),
    url(r'friend/decline/(?P<request_id>\d+)/$', views.friend_decline),

    url(r'relation/accept/(?P<relation_id>\d+)/$', views.relation_accept),
    url(r'relation/decline/(?P<relation_id>\d+)/$', views.relation_decline),

    url(r'unfollow/$', views.unfollow),
    url(r'follow/$', views.follow),

    url(r'hide/$', views.hide_friend),
    url(r'filter/add/$', views.filter_add),
    url(r'filter/remove/$', views.filter_remove),
)
