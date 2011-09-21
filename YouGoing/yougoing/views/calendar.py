'''
Created on 16.6.2011

@author: MuZeR
'''
from yougoing.baseview import BaseView
class CalendarView(BaseView):
    template = "calendar.djhtml"
    def get(self, request):
        pass
    
    
class CalendarEventsView(BaseView):
    template = "formats/json.djhtml"
    def get(self, request, id):
        start_time = request.GET['start']
        end_time = request.GET['end']
        print start_time + ":" + end_time
        json_data = '''
        [
            { "id": 1, "title": "Event 1", "start": "2011-06-16T10:00", "end": "2011-06-16T12:00", "allDay": false }
        ]
        '''
        self.context = {'json': json_data}
        
    def post(self, request, id):
        start_time = request.POST["start"]
        end_time = request.POST["end"]
        print start_time + ":" + end_time