from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import ProfileForm, UserLoginForm, UserRegisterForm
from .models import Profile


class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'


def register(request):
    form = UserRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        Profile.objects.get_or_create(user=user)
        login(request, user)
        messages.success(request, 'Welcome to Automart 2025!')
        return redirect('dashboard:home')
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile_obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})
