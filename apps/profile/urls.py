from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'feed/$', views.feed),
    url(r'timeline/$', views.timeline),
    url(r'settings/$', views.settings),
    url(r'filter/add/$', views.filter_add),
    url(r'filter/remove/$', views.filter_remove),
    url(r'profile/$', views.profile),
    url(r'profile/albums/$', views.albums),
    url(r'profile/albums/album_create/$', views.album_create),
    url(r'profile/albums/album_name/$', views.change_album_name),
    url(r'profile/albums/change_position/$', views.album_postion),
    url(r'profile/albums/delete_album/$', views.delete_album),
    url(r'profile/albums/(?P<album_id>\d+)/$', views.album_posts),
    url(r'profile/delete/$', views.delete_profile),
    url(r'profile/reset_picture/$', views.reset_picture),
    url(r'profile/(?P<username>\w+)/$', views.profile),
    url(r'profile/(?P<username>\w+)/related/$', views.related_users),
    url(r'profile/(?P<username>\w+)/image/$', views.profile_image),
    url(r'profile/(?P<username>\w+)/albums/$', views.albums, name="users-albums"),
)
