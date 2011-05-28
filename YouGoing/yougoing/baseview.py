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

# Simple E-mail address validation
# not compatible with RFC 822 because it requires HUGE
# reg exp, but "should" be enough
# TODO: Use Django's own EmailField, if ever deploy for real use
    

class BaseView(object):
    def __call__(self, request, *args, **kwargs):
        """
            Call trough method to enable use of methods as
            handlers instead of checking request.method
            in each handler function. Also enables default
            handler for unused methods which the user doesn't
            have to implement for each handler.
        """
        self._request = request
        self._user = get_logged_in_user(request)
        try:
            if request.method == "GET":
                return self._get(request, *args, **kwargs)
            elif request.method == "POST":
                return self._post(request, *args, **kwargs)
            elif request.method == "PUT":
                return self._post(request, *args, **kwargs)
            elif request.method == "DELETE":
                return self._post(request, *args, **kwargs)
            else:
                print "Unknown method: %s" % (request.method)
                return HttpResponseNotFound()
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
            
    def _get(self, request):
        print "GET not implemented"
        return HttpResponseNotFound()
    def _post(self, request):
        print "POST not implemented"
        return HttpResponseNotFound()
    def _put(self, request):
        print "PUT not implemented"
        return HttpResponseNotFound()
    def _delete(self, request):
        print "DELETE not implemented"
        return HttpResponseNotFound()
    
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
        