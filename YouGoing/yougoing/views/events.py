'''
Created on 29.6.2011

@author: MuZeR
'''
from yougoing.models import Event, map_values
from yougoing.baseview import BaseView
class CalendarView(BaseView):
    template = "calendar.djhtml"
    def get(self, request):
        pass

    
class CalendarEventsView(BaseView):
    template = "event/create_event.djhtml"
    def get(self, request):
        pass
        
    def post(self, request):
        pass

from django import forms

class EventForm(forms.Form):
    name = forms.CharField(max_length=255,required=True)
    is_public = forms.BooleanField(required=False, initial=False)
    
    description = forms.CharField(max_length=2047,widget=forms.Textarea(attrs={"cols":30,"rows":4}),required=False)
    coordinates = forms.CharField(max_length=32,required=False)
    address = forms.CharField(max_length=255,widget=forms.Textarea(attrs={"cols":30,"rows":4}),required=False)
    
    start_date = forms.DateField()
    start_time = forms.TimeField()
    end_date = forms.DateField()
    end_time = forms.TimeField()


class EventView(BaseView):
    template = "event/view_event.djhtml"
    
    def get(self, request, event_id, secret_key=None):
        event = Event.get_event(event_id, request.user, secret_key)
        form = EventForm(initial=event.event_to_dict())
        self.add_to_context("event", event)
        self.add_to_context("form", form)
    def post(self, request, event_id):
        pass

    
    

class CreateEventView(BaseView):
    template = "event/create_event.djhtml"
    
    def get(self, request):
        self.add_to_context("form", EventForm())
        
    def post(self, request):
        form = EventForm(request.POST)
        self.add_to_context("form", form)
        if form.is_valid():
            event = Event.create_event(request.user, form)
            self.redirect(view="view_event", event_id=event.id)
    
    
        