from django.conf.urls.defaults import patterns, url
import views


urlpatterns = patterns('',
    url(r'^browse/$', views.page_browsing),
    url(r'^browse/(?P<page_type>\w+)/$', views.page_browsing, name="page-browse"),
    url(r'^comments_event_pagination/(?P<event_id>\d+)/(?P<page>\d+)/$', views.comments_event_pagination),
    url(r'^feedback/$', views.feedback),
    url(r'^feedback/agree/(?P<item_id>\d+)/$', views.count_agrees),
    url(r'^feedback/disagree/(?P<item_id>\d+)/$', views.count_disagrees),
    url(r'^leaderboard/$', views.leaderboard),
    url(r'^leaderboard/(?P<cat_id>\d+)/$', views.save_browsing_categories),
    url(r'^love_count/$', views.love_count),
    url(r'^update/$', views.update),
)

