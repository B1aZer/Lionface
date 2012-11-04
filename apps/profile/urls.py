from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('profile.views',
    url(r'^(?P<username>\w+)/delete/$', 'delete_profile'),
    url(r'^(?P<username>\w+)/reset_picture/$', 'reset_picture'),
    url(r'^(?P<username>\w+)/account/$', 'settings'),

    url(r'^(?P<username>\w+)/feed/$', 'feed'),
    url(r'^(?P<username>\w+)/related/$', 'related_users'),
    url(r'^(?P<username>\w+)/image/$', 'profile_image'),
    url(r'^(?P<username>\w+)/image/more/$', 'profile_image_more', name='profile-image-more'),
    url(r'^(?P<username>\w+)/image/primary/$', 'profile_image_primary', name='profile-image-primary'),
    url(r'^(?P<username>\w+)/image/delete/$', 'profile_image_delete', name='profile-image-delete'),
    url(r'^(?P<username>\w+)/albums/$', 'albums', name="users-albums"),
    url(r'^(?P<username>\w+)/albums/(?P<album_id>\d+)/$', 'album_posts', name="users-albums-posts"),

    url(r'^(?P<username>\w+)/albums/album_create/$', 'album_create'),
    url(r'^(?P<username>\w+)/albums/album_name/$', 'change_album_name'),
    url(r'^(?P<username>\w+)/albums/change_position/$', 'album_postion'),
    url(r'^(?P<username>\w+)/albums/delete_album/$', 'delete_album'),

    url(r'^(?P<username>\w+)/loves/$', 'loves', name="user-loves"),

    url(r'^(?P<username>\w+)/$', 'profile', name="provile-view"),

)
