from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^business/$', views.main),
    url(r'^leaderboard/$', views.leaderboard),
    url(r'^nonprofit/$', views.nonprofit),
    url(r'^page/(?P<slug>\w+)/$', views.page),
)

