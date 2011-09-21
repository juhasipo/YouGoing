'''
Created on 27.5.2011

@author: MuZeR
'''

from yougoing.baseview import BaseView
    
class MobileView(BaseView):
    template = "mobile.djhtml"
    login_required = ["GET", "POST"]
    
    def get(self, request, event_name = "New event"):
        if request.mobile:
            p = "Mobile"
        else:
            p = "Desktop"
        self.add_to_context("event_name", p)
        