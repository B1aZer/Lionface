from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'timeline/$', views.timeline),
    url(r'settings/$', views.settings),
    url(r'block/$', views.hide_friend),
    url(r'filter/add/$', views.filter_add),
    url(r'filter/remove/$', views.filter_remove),
    url(r'(?P<username>\w+)/delete/$', views.delete_profile),
    url(r'(?P<username>\w+)/reset_picture/$', views.reset_picture),

    url(r'(?P<username>\w+)/feed/$', views.feed),
    url(r'(?P<username>\w+)/related/$', views.related_users),
    url(r'(?P<username>\w+)/image/$', views.profile_image),
    url(r'(?P<username>\w+)/albums/$', views.albums, name="users-albums"),
    url(r'(?P<username>\w+)/albums/(?P<album_id>\d+)/$', views.album_posts, name="users-albums-posts"),

    url(r'(?P<username>\w+)/albums/album_create/$', views.album_create),
    url(r'(?P<username>\w+)/albums/album_name/$', views.change_album_name),
    url(r'(?P<username>\w+)/albums/change_position/$', views.album_postion),
    url(r'(?P<username>\w+)/albums/delete_album/$', views.delete_album),

    url(r'(?P<username>\w+)/$', views.profile, name="provile-view"),
)
