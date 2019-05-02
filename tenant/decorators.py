from django.core.exceptions import PermissionDenied
from tenant.models import TblAgent
from django.shortcuts import render


def for_admin(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
           return function(request, *args, **kwargs)
        else:
            return render(request,'Base.html') 
    return wrap

def for_staff(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
           return function(request, *args, **kwargs)
        else:
            return render(request,'Base.html') 
    return wrap