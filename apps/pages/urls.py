from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^browse/$', views.page_browsing),
    url(r'^browse/(?P<page_type>\w+)/$', views.page_browsing, name="page-browse"),
    url(r'^business/$', views.main),
    url(r'^business/(?P<slug>\w+)/$', views.page, name="business-page"),
    url(r'^business/(?P<slug>\w+)/list_posts/$', views.list_posts),
    url(r'^business/(?P<slug>\w+)/reposition/$', views.reposition),
    url(r'^leaderboard/$', views.leaderboard),
    url(r'^love_count/$', views.love_count),
    url(r'^nonprofit/$', views.nonprofit),
    url(r'^nonprofit/(?P<slug>\w+)/$', views.page, name="nonprofit-page"),
    url(r'^nonprofit/(?P<slug>\w+)/list_posts/$', views.list_posts),
    url(r'^nonprofit/(?P<slug>\w+)/reposition/$', views.reposition),
    url(r'^page/(?P<slug>\w+)/$', views.page),
    url(r'^page/(?P<slug>\w+)/delete_page/$', views.delete_page),
    url(r'^page/(?P<slug>\w+)/list_posts/$', views.list_posts),
    url(r'^page/(?P<slug>\w+)/reset_picture/$', views.reset_picture),
    url(r'^page/(?P<slug>\w+)/page_content/$', views.page_content),
    url(r'^page/(?P<slug>\w+)/settings/$', views.settings),
    url(r'^page/(?P<slug>\w+)/settings_admins/$', views.settings_admins),
    url(r'^update/$', views.update),
)

