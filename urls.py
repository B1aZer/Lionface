from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from haystack.views import SearchView, search_view_factory
import search.forms
import search.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'lionface.views.home', name='home'),
    # url(r'^lionface/', include('lionface.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', 'account.views.home', name='home'),
    url(r'^terms/$', 'public.views.terms'),
    url(r'^privacy/$', 'public.views.privacy'),
    url(r'^about/$', 'public.views.about'),
    url(r'^feedback/$', 'public.views.feedback'),
    url(r'^account/', include('account.urls')),
    url(r'^user/', include('profile.urls')),
    url(r'^notifications/', include('notification.urls')),
    url(r'^posts/', include('post.urls')),
    url(r'^search/', login_required(search_view_factory(
        #view_class=SearchView,
            view_class=search.views.CustumSearchView,
            form_class=search.forms.SearchForm,
        ))),
)
