'''
Created on 29.6.2011

@author: MuZeR
'''
from yougoing.baseview import BaseView
class CalendarView(BaseView):
    template = "calendar.html"
    def get(self, request):
        pass

    
class CalendarEventsView(BaseView):
    template = "desktop/create_event.html"
    def get(self, request):
        pass
        
    def post(self, request):
        pass