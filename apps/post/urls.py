from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'love/$', views.love),
    url(r'change_settings/$', views.change_settings),
    url(r'del/(?P<post_id>\d+)/$', views.delete),
    url(r'dlcom/(?P<message_id>\d+)/$', views.delete_own_comment),
    url(r'feed/$', views.feed),
    url(r'feed/(?P<user_id>\d+)/$', views.feed),
    url(r'follow/$', views.follow),
    url(r'save/$', views.save),
    url(r'show/$', views.show),
    url(r'share/(?P<post_id>\d+)/$', views.share),
    url(r'tags/(?P<tag_id>\d+)/$', views.tag_feed),
    url(r'test/$', views.test),
    url(r'timeline/(?P<post_num>\d+)/$', views.timeline),
    url(r'toggle_privacy/$', views.toggle_privacy),
    url(r'images/ajax/comments/$', views.images_comments_ajax,
        name='post_images_ajax_comments'),
    url(r'images/ajax/rotate/$', views.rotate_image),
    url(r'(?P<post_id>\d+)/comments_page/(?P<page>\d+)/$', views.comments_pagination),
)
