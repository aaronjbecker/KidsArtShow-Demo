from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import View
from .forms import loginForm, registerForm
from .models import UserAccount
from arts.models import Art
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
                print('logged in user:'+ the_user.username)

                return HttpResponseRedirect('/accounts/')
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
        user = authenticate(username=new_user.username,
                            password=password)
        login(request, user)
        return HttpResponseRedirect('/accounts/')
    context = {'form':form,
               'view_url': view_url}
    return render(request,'accounts/authform.html',context)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


class UserDashboard(View):
    def get(self, request, *args, **kwargs):
        context={}
        account = self.request.user
        print(account)
        arts = Art.objects.filter(user = account)
        context['arts'] = arts

        return render(request, 'accounts/userdashboard.html',context)


