'''
Created on 29.6.2011

@author: MuZeR
'''
from yougoing.models import Event
from yougoing.baseview import BaseView
class CalendarView(BaseView):
    template = "calendar.djhtml"
    def get(self, request):
        pass

    
class CalendarEventsView(BaseView):
    template = "desktop/create_event.djhtml"
    def get(self, request):
        pass
        
    def post(self, request):
        pass

class EventView(BaseView):
    
    template = "event/view_event.djhtml"
    
    def get(self, request, event_id, secret_key=None):
        event = Event.get_event(event_id, request.user, secret_key)
        self.add_to_context("event", event)

from django import forms

class EventForm(forms.Form):
    name = forms.CharField(max_length=255,required=True)
    is_public = forms.BooleanField()
    
    

class CreateEventView(BaseView):
    use_env_template = True
    template = "create_event.djhtml"
    
    def get(self, request):
        self.add_to_context("form", EventForm())
    
    def post(self, request):
        event = Event.create_event(request.user, "Foo", False)
        self.add_to_context("event", event)
        self.template = "event/view_event.djhtml"
        self.use_env_template = False
    
    
    
        