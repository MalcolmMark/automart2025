from django.contrib import messages
from django.shortcuts import render, redirect

from cars.models import Car
from .forms import ContactForm


def home(request):
    featured_cars = Car.objects.filter(is_approved=True)[:6]
    return render(request, 'core/home.html', {'featured_cars': featured_cars})


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your message has been sent successfully.')
        return redirect('core:contact')
    return render(request, 'core/contact.html', {'form': form})


def custom_404(request, exception):
    return render(request, 'core/404.html', status=404)


def custom_500(request):
    return render(request, 'core/500.html', status=500)
