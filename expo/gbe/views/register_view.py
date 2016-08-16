from django.contrib.auth import (
    authenticate,
    login,
)
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from expo.gbe_logging import log_func
from gbe.forms import UserCreateForm


@log_func
def RegisterView(request):
    '''
    Allow a user to register with gbe. This should create both a user
    object and a profile. Currently, creates only the user object
    (profile produced by "update_profile")
    '''
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            username = form.clean_username()
            password = form.clean_password2()
            form.save()
            user = authenticate(username=username,
                                password=password)
            login(request, user)
            return HttpResponseRedirect(reverse('profile_update',
                                                urlconf='gbe.urls'))
    else:
        form = UserCreateForm()
    return render(request, 'gbe/register.tmpl', {'form': form})
