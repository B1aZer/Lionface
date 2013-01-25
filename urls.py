from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from haystack.views import SearchView, search_view_factory
from haystack.forms import ModelSearchForm, SearchForm
import search.forms
import search.views
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import socketio.sdjango
from chat.views import HomeView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'lionface.views.home', name='home'),
    # url(r'^lionface/', include('lionface.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^administration/', include(admin.site.urls)),

    url(r'^$', 'account.views.home', name='home'),
    url(r'^micro/$', 'public.views.micro'),
    url(r'^terms/$', 'public.views.terms'),
    url(r'^privacy/$', 'public.views.privacy'),
    url(r'^about/$', 'public.views.about'),
    url(r'^feedback/$', 'public.views.feedback'),
    #url(r'^404/$', 'public.views.page404'),
    #url(r'^500/$', 'public.views.page500'),
    url(r'^account/', include('account.urls')),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^posts/', include('post.urls')),
    url(r'^tags/', include('tags.urls')),
    url(r'^check/', include('comet.urls')),
    url(r'^search/', login_required(search_view_factory(
        #view_class=SearchView,
            view_class=search.views.CustumSearchView,
            form_class=search.forms.SearchForm,
        ))),
    url(r'^search_ajax/', login_required(search_view_factory(
        #view_class=SearchView,
            template='search/search_ajax.html',
            view_class=search.views.CustumSearchView,
            form_class=search.forms.SearchForm,
        ))),
    url(r'^tag/', login_required(search_view_factory(
        #view_class=SearchView,
            template='search/search_tags.html',
            view_class=SearchView,
            form_class=search.forms.TagSearchForm,
        ))),
    url(r'^auto/', 'search.views.auto_complete'),
    url(r'^auto_calendar/(?P<slug>\w+)/', 'search.views.auto_calendar'),
    url(r'^auto_discussions/(?P<slug>\w+)/', 'search.views.auto_discussions'),
    url(r'^auto_favourite_pages/', 'search.views.auto_fav_pages'),
    url(r'^auto_pages/(?P<slug>\w+)/', 'search.views.auto_pages'),
    url(r'^auto_relation/', 'search.views.auto_relation'),
    url(r'^import/$', include('smileys.urls')),
    url(r'^pages/', include('pages.urls')),
    url(r'^images/', include('images.urls')),
    url(r'^schools/', include('schools.urls')),
    url(r'^discussions/', 'discussions.views.home'),
    #url(r'^socket\.io', 'chat.views.socketio_service', name='socketio_service'),
    url("^socket\.io", include(socketio.sdjango.urls)),
    url("^chat/", HomeView.as_view()),
    url(r'^(?P<username>\w+)/notifications/', include('notification.urls')),
    url(r'^(?P<username>\w+)/messages/', include('messaging.urls')),
)

urlpatterns += patterns('',
    url(r'', include('profile.urls')),
)

# ... the rest of your URLconf goes here ...

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.UPLOAD_DIR,
        }),
   )

