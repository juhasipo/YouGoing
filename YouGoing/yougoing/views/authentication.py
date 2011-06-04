'''
Created on 4.6.2011

@author: JPS
'''

from yougoing.baseview import BaseView
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.http import HttpResponseRedirect

class LoginForm(forms.Form):
    my_username = forms.CharField(max_length=10)
    my_password = forms.CharField(widget=forms.PasswordInput)

class DoLogin(BaseView):
    template = 'login.html'
    
    def get(self, request):
        # Logout first
        logout(request)
        
        form = LoginForm() # An unbound form
        
        next = '/'
        try:
            next = request.GET['next']
        except:
            pass
        self.context = {'form': form, 'next': next}
        
    def post(self, request):
        # Logout first
        logout(request)
        
        form = LoginForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            username = form.cleaned_data['my_username']
            password = form.cleaned_data['my_password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
            
                path = '/'
                try:
                    path = request.POST['next']
                except:
                    pass
                self.redirect_to = path # Redirect after POST
                return
        
        next = '/'
        try:
            next = request.GET['next']
        except:
            pass
        self.context = {'form': form, 'next': next}

class DoLogout(BaseView):
    def get(self,request):
        logout(request)
        # Return user to main page
        self.redirect_to = '/'

'''
def register(request):
    # Logout first
    logout(request)
    
    if request.method == 'POST': # If the form has been submitted...
        form = UserCreationForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = User.objects.create_user(username=username,email='',password=password)
            # Additional user data could be created here
            
            return HttpResponseRedirect('/login') # Redirect after POST
    else:
        form = UserCreationForm() # An unbound form

    return render_page('register.html', request, {'form': form }, True)
'''