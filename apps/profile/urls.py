from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('profile.views',
    url(r'^(?P<username>\w+)/delete/$', 'delete_profile'),
    url(r'^(?P<username>\w+)/account/$', 'settings'),
    url(r'^(?P<username>\w+)/send_message/$', 'send_message'),

    url(r'^(?P<username>\w+)/add_bio_info/$', 'save_bio_info'),
    url(r'^(?P<username>\w+)/add_birth_date/$', 'save_birth_date'),
    url(r'^(?P<username>\w+)/add_favourite_pages/$', 'add_favourite_pages'),
    url(r'^(?P<username>\w+)/add_relation/$', 'add_relation'),
    url(r'^(?P<username>\w+)/add_url_field/$', 'save_url_field'),
    url(r'^(?P<username>\w+)/del_favourite_page/(?P<page_id>\d+)$', 'remove_favourite_page'),
    url(r'^(?P<username>\w+)/feed/$', 'feed'),
    url(r'^(?P<username>\w+)/favourites_reposition/$', 'favourites_reposition'),
    url(r'^(?P<username>\w+)/related/$', 'related_users'),
    url(r'^(?P<username>\w+)/reset_picture/$', 'reset_picture'),
    url(r'^(?P<username>\w+)/reposition/$', 'reposition'),
    url(r'^(?P<username>\w+)/images/$', 'images'),
    url(r'^(?P<username>\w+)/images/reset/$', 'images_reset'),
    url(r'^(?P<username>\w+)/images/ajax/$', 'images_ajax'),
    url(r'^(?P<username>\w+)/images/ajax/comments/$', 'images_comments_ajax'),
    url(r'^(?P<username>\w+)/images/ajax/quote/$', 'images_quote_ajax',
        name="profile-images-quote"),
    url(r'^(?P<username>\w+)/albums/$', 'albums', name="users-albums"),
    url(r'^(?P<username>\w+)/albums/(?P<album_id>\d+)/$', 'album_posts',
        name="users-albums-posts"),

    url(r'^(?P<username>\w+)/albums/album_create/$', 'album_create'),
    url(r'^(?P<username>\w+)/albums/album_name/$', 'change_album_name'),
    url(r'^(?P<username>\w+)/albums/change_position/$', 'album_postion'),
    url(r'^(?P<username>\w+)/albums/delete_album/$', 'delete_album'),

    url(r'^(?P<username>\w+)/loves/$', 'loves', name="user-loves"),

    url(r'^(?P<username>\w+)/$', 'profile', name="provile-view"),
)
