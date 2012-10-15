from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^page/$', views.page),
    url(r'^leaderboard/$', views.leaderboard),
    url(r'^nonprofit/$', views.nonprofit),
    url(r'^business/$', views.main),
)

