from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UesrRegisterForm

def register(request):
    if request.method == 'POST':
        form = UesrRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('kids-art-show-home')
    else:
        form = UesrRegisterForm()
    return render(request, 'users/register.html', {'form' : form})
