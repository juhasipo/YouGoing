'''
Created on 27.5.2011

@author: MuZeR
'''

from yougoing.baseview import BaseView

class MobileView(BaseView):
    def get(self, request, event_name):
        return self.render_template("mobile.html", {"event_name": event_name})