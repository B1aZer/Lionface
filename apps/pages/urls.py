from django.conf.urls.defaults import patterns, url
import views


urlpatterns = patterns('',
    url(r'^browse/$', views.page_browsing),
    url(r'^browse/(?P<page_type>\w+)/$', views.page_browsing, name="page-browse"),
    url(r'^business/$', views.main),
    url(r'^business/(?P<slug>\w+)/$', views.page, name="business-page"),
    url(r'^business/(?P<slug>\w+)/list_posts/$', views.list_posts),
    url(r'^business/(?P<slug>\w+)/list_feedback/$', views.list_feedback),
    url(r'^business/(?P<slug>\w+)/reposition/$', views.reposition),
    url(r'^business/(?P<slug>\w+)/friends_position/$', views.friends_position),
    url(r'^business/(?P<slug>\w+)/community_check/$', views.community_check),
    url(r'^business/(?P<slug>\w+)/community_text/$', views.community_text),
    url(r'^business/(?P<slug>\w+)/community_date/$', views.community_date),
    url(r'^feedback/$', views.feedback),
    url(r'^feedback/agree/(?P<item_id>\d+)/$', views.count_agrees),
    url(r'^feedback/disagree/(?P<item_id>\d+)/$', views.count_disagrees),
    url(r'^leaderboard/$', views.leaderboard),
    url(r'^love_count/$', views.love_count),
    url(r'^nonprofit/$', views.nonprofit),
    url(r'^nonprofit/(?P<slug>\w+)/$', views.page, name="nonprofit-page"),
    url(r'^nonprofit/(?P<slug>\w+)/list_posts/$', views.list_posts),
    url(r'^nonprofit/(?P<slug>\w+)/list_feedback/$', views.list_feedback),
    url(r'^nonprofit/(?P<slug>\w+)/reposition/$', views.reposition),
    url(r'^nonprofit/(?P<slug>\w+)/friends_position/$', views.friends_position),
    url(r'^nonprofit/(?P<slug>\w+)/community_check/$', views.community_check),
    url(r'^nonprofit/(?P<slug>\w+)/community_text/$', views.community_text),
    url(r'^nonprofit/(?P<slug>\w+)/community_date/$', views.community_date),
    url(r'^page/(?P<slug>\w+)/$', views.page),
    url(r'^page/(?P<slug>\w+)/accept_request/(?P<request_id>\d+)/$', views.accept_friend_request),
    url(r'^page/(?P<slug>\w+)/confirm_comm_request/(?P<request_id>\d+)/$', views.accept_community_request),
    url(r'^page/(?P<slug>\w+)/decline_comm_request/(?P<request_id>\d+)/$', views.decline_community_request),
    url(r'^page/(?P<slug>\w+)/decline_request/(?P<request_id>\d+)/$', views.decline_friend_request),
    url(r'^page/(?P<slug>\w+)/delete_page/$', views.delete_page),
    url(r'^page/(?P<slug>\w+)/events/add/$', views.add_events),
    url(r'^page/(?P<slug>\w+)/events/form/$', views.event_comments),
    url(r'^page/(?P<slug>\w+)/events/get/$', views.get_events),
    url(r'^page/(?P<slug>\w+)/events/share/$', views.share_event),
    url(r'^page/(?P<slug>\w+)/events/update/$', views.post_update_change),
    url(r'^page/(?P<slug>\w+)/hide_request/(?P<request_id>\d+)/$', views.hide_friend_request),
    url(r'^page/(?P<slug>\w+)/list_posts/$', views.list_posts),
    url(r'^page/(?P<slug>\w+)/list_feedback/$', views.list_feedback),
    url(r'^page/(?P<slug>\w+)/members/$', views.page_members),
    url(r'^page/(?P<slug>\w+)/members/(?P<member_id>\d+)/$', views.page_members),
    url(r'^page/(?P<slug>\w+)/page_content/$', views.page_content),
    url(r'^page/(?P<slug>\w+)/remove_friend/$', views.remove_friend_page),
    url(r'^page/(?P<slug>\w+)/reset_picture/$', views.reset_picture),
    url(r'^page/(?P<slug>\w+)/reset_album_activity/$', views.reset_album_activity),
    url(r'^page/(?P<slug>\w+)/settings/$', views.settings),
    url(r'^page/(?P<slug>\w+)/settings_admins/$', views.settings_admins),
    url(r'^page/(?P<slug>\w+)/send_request/$', views.send_friend_request),
    url(r'^page/(?P<slug>\w+)/images/$', views.images),
    url(r'^page/(?P<slug>\w+)/images/ajax/$', views.images_ajax),
    url(r'^page/(?P<slug>\w+)/images/ajax/comments/$', views.images_comments_ajax),
    url(r'^update/$', views.update),
)

