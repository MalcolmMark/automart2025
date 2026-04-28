from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User

from cars.models import Car, Favourite, Inquiry, Brand, Category
from core.models import ContactMessage


@login_required
def home(request):
    stats = {
        'my_listings': Car.objects.filter(seller=request.user).count(),
        'saved_cars': Favourite.objects.filter(user=request.user).count(),
        'inquiries': Inquiry.objects.filter(car__seller=request.user).count(),
    }
    return render(request, 'dashboard/home.html', {'stats': stats})


@login_required
def my_listings(request):
    listings = Car.objects.filter(seller=request.user)
    return render(request, 'dashboard/my_listings.html', {'listings': listings})


@login_required
def saved_cars(request):
    saved = Favourite.objects.select_related('car').filter(user=request.user)
    return render(request, 'dashboard/saved_cars.html', {'saved': saved})


@login_required
def inquiries(request):
    inquiry_list = Inquiry.objects.select_related('car', 'sender').filter(car__seller=request.user)
    return render(request, 'dashboard/inquiries.html', {'inquiries': inquiry_list})


@staff_member_required
def admin_panel(request):
    context = {
        'users_count': User.objects.count(),
        'cars_count': Car.objects.count(),
        'pending_count': Car.objects.filter(is_approved=False).count(),
        'brands_count': Brand.objects.count(),
        'categories_count': Category.objects.count(),
        'messages_count': ContactMessage.objects.count(),
    }
    return render(request, 'adminpanel/dashboard.html', context)
