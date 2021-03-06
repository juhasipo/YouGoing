from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from yougoing.views import mobile, calendar, main
from yougoing.views import authentication
from yougoing.views import events
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'YouGoing.views.home', name='home'),
    # url(r'^YouGoing/', include('YouGoing.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', main.MainView, name="index"),
    url(r'^mobile/(?P<event_name>\w+)$', mobile.MobileView, name="mobile"),
    url(r'^calendar/$', calendar.CalendarView, name="calendar"),
    url(r'^calendar/(?P<id>\d+)$', calendar.CalendarEventsView, name="calendar_events"),
    url(r'^event/new$', events.CreateEventView, name="new_event"),
    url(r'^event/answer/(?P<event_id>\d+)/(?P<secret_key>\w*)', main.MainView, name="answer_event"),
    url(r'^event/(?P<event_id>\d+)$', events.EventView, name="view_event"),
    url(r'^event/(?P<event_id>\d+)/(?P<secret_key>\w*)$', events.EventView, name="view_event"),
    url(r'^event/(?P<event_id>\d+)$', events.EventView, name="edit_event"),
    
    # User management
    url(r'^login/$', authentication.DoLogin, name="login"),
    url(r'^logout/$', authentication.DoLogout, name="logout"),
    #url(r'^register/$', 'project.views.register'),
)
