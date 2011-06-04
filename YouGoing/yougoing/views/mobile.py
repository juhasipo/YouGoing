'''
Created on 27.5.2011

@author: MuZeR
'''

from yougoing.baseview import BaseView

def test_view(request):
    print "A"
    for i in xrange(0,2**28):
        pass
    print "B"
    
class MobileView(BaseView):
    template = "mobile.html"
    login_required = ["GET", "POST"]
    
    def get(self, request, event_name):
        if request.mobile:
            p = "Mobile"
        else:
            p = "Desktop"
        self.add_to_context("event_name", p)
        