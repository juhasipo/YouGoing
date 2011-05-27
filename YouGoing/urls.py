from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from yougoing.views import mobile
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'YouGoing.views.home', name='home'),
    # url(r'^YouGoing/', include('YouGoing.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', mobile.MobileView(), name="index"),
    url(r'^mobile/(?P<event_name>\w+)$', mobile.MobileView(), name="mobile"),
)
