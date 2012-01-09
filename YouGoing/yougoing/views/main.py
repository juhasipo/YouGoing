'''
Created on 21.9.2011

@author: Juha
'''
from yougoing.baseview import BaseView
from yougoing.models import Event

class MainView(BaseView):
    login_required = ["GET", "POST"]
    
    def get(self, request, event_name = "New event"):
        if request.mobile:
            prefix = "mobile/"
        else:
            prefix = "desktop/"
        self.template = prefix + "main.djhtml"
        self.add_to_context("user_events", Event.get_user_events(self.get_user()))
        self.add_to_context("user", self.get_user())
        