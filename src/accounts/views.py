from django.shortcuts import render, HttpResponseRedirect

from .forms import loginForm, registerForm
from django.contrib.auth import get_user_model, authenticate, login, logout

User = get_user_model()

def login_view(request):
    form = loginForm(request.POST or None)
    view_url = request.path
    if form.is_valid():
        username_email = form.cleaned_data['username']
        password = form.cleaned_data['password']
        try:
            the_user = User.objects.get(username = username_email)
        except User.DoesNotExist:
            the_user = User.objects.get(email=username_email)
        except:
            the_user = None
        if the_user is not None:
            user = authenticate(username=the_user.username,
                                password=password)
            if user.is_active:
                login(request, user)
                print('logged in')
                return HttpResponseRedirect('/arts/')
            else:
                pass
        else:
            return HttpResponseRedirect('/register/')
    context = {'form':form,
               'view_url':view_url}
    return render(request,'accounts/authform.html',context)

def register_view(request):
    form = registerForm(request.POST or None)
    view_url = ''
    if form.is_valid():
        view_url = request.path
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        new_user = User.objects.create_user(username,email,password)
        return HttpResponseRedirect('/arts/')
    context = {'form':form,
               'view_url': view_url}
    return render(request,'accounts/authform.html',context)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

