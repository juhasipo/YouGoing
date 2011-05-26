# Create your views here.
from django.http import HttpResponse, HttpResponseNotFound,\
    HttpResponseForbidden, HttpResponseRedirect, HttpResponseServerError,\
    HttpResponseBadRequest, HttpResponseRedirect
    
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout


def index(request):
    return HttpResponseForbidden("Under construction")
