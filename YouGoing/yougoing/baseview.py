'''
Created on 12.1.2011

@author: MuZeR
'''

from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponseRedirect
from django.template import RequestContext, loader
import settings
from yougoing.utils.exceptions import ForbiddenView
from yougoing.utils.security import get_logged_in_user
from django.contrib import messages
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse

class BaseView(object):
    def __new__(cls, request, *args, **kwargs):
        """
            Called when Django has resolved URL and
            calls the view. Creates new view object
            and handles request using that new object
        """
        view = cls._new_object_by_type(request, *args, **kwargs)
        return view.handle_request(request, *args, **kwargs)
    
    @classmethod
    def _new_object_by_type(cls, *args, **kwargs):
        """
            Creates new instance of the given object,
            initializes and returns it.
        """
        obj = object.__new__(cls)
        obj.__init__(*args, **kwargs)
        return obj
    
    def __init__(self, *args, **kwargs):
        self._request = None
        self._user = None
        self.context = {}
        self.errors = []
        self.warnings = []
    
    def add_to_context(self, key, value):
        self.context[key] = value
    def set_errors(self, error_list):
        self.errors = error_list
    def add_to_errors(self, error):
        self.error.append(error)
    def set_warnings(self, warning_list):
        self.errors = warning_list
    def add_to_warnings(self, warning):
        self.error.append(warning)
    
    
    def handle_request(self, request, *args, **kwargs):
        """
            Handles the given request. Dispatches the
            request to the correct handler method. Also
            sets user object to current user if a user
            has logged in.
        """
        self._request = request
        self._user = get_logged_in_user(request)
        try:
            if request.method == "GET":
                self.get(request, *args, **kwargs)
            elif request.method == "POST":
                self.post(request, *args, **kwargs)
            elif request.method == "PUT":
                self.post(request, *args, **kwargs)
            elif request.method == "DELETE":
                self.post(request, *args, **kwargs)
            else:
                print "Unknown method: %s" % (request.method)
                return HttpResponseNotFound()
            return self.handle_response()
        except ForbiddenView, e:
            if self.get_user() == None:
                request.session['redirect_after_login'] = request.build_absolute_uri()
                return self.redirect_to_view("login")
            else:
                return self.render_template(template='error.html',  \
                                        context={}, \
                                        response=HttpResponseServerError, \
                                        errors=[_("Forbidden")])
        except Exception, e:
            # In debug mode, show the trace
            if settings.DEBUG:
                raise
            # Else just show an error page
            return self.render_template(template='error.html',  \
                                        context={}, \
                                        response=HttpResponseServerError, \
                                        errors=[unicode(e)])
    def get_user(self):
        return self._user
            
    def get(self, request):
        print "GET not implemented"
        return HttpResponseNotFound()
    def post(self, request):
        print "POST not implemented"
        return HttpResponseNotFound()
    def put(self, request):
        print "PUT not implemented"
        return HttpResponseNotFound()
    def delete(self, request):
        print "DELETE not implemented"
        return HttpResponseNotFound()
    
    def handle_response(self):
        if not hasattr(self, "template"):
            raise Exception("No template set")
        
        if not hasattr(self, "response") == None:
            self.response = HttpResponse
        
        self.context["errors"] = self.errors
        self.context["warnings"] = self.warnings
        self.context["user"] = self.get_user()
        
        t = loader.get_template(self.template)
        self.context.update(csrf(self._request))
        c = RequestContext(self._request, self.context)
        return self.response(t.render(c))
    
    def render_template(self, template, context, response=None, errors=[], warnings=[]):
        """
            @param template: Name of the template
            @param context: Context for the template as dictionary
            @param response: Response object to use, Default: HttpResponse
            @param errors: List of errors as string
            @param warnings: List of warnings as string
        """
        t = loader.get_template(template)
        context["errors"] = errors
        context["warnings"] = warnings
        if not "member" in context:
            context["member"] = self.get_user()
        context.update(csrf(self._request))
        c = RequestContext(self._request, context)
        
        if response == None:
            return HttpResponse(t.render(c))
        else:
            return response(t.render(c))
        
    def redirect(self, to):
        return HttpResponseRedirect(to)
    
    def redirect_to_view(self, view, args = None, kwargs = None):
        return HttpResponseRedirect(reverse(view, None, args, kwargs))
    
    def require_user_logged_in(self,user):
        """ 
            Helper method for authorization 
            @raise ForbiddenView if user not logged in
        """
        if user == None:
            raise ForbiddenView("User not logged in")
    
    def add_info_message(self, message):
        self.add_message(messages.INFO, message)
    def add_warning_message(self, message):
        self.add_message(messages.WARNING, message)
    def add_error_message(self, message):
        self.add_message(messages.ERROR, message)
    
    def add_message(self, level, message):
        print "message %s level %d" % (message, level)
        if self._request == None:
            print "No request"
        messages.add_message(self._request, level, message)
        