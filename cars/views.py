from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm, CarForm, InquiryForm, ReviewForm
from .models import Booking, Brand, Car, Category, Favourite, Inquiry


def listing(request):
    cars = Car.objects.filter(is_approved=True)
    q = request.GET.get('q', '')
    if q:
        cars = cars.filter(Q(title__icontains=q) | Q(model__icontains=q) | Q(brand__name__icontains=q))

    for field in ['brand', 'fuel_type', 'transmission', 'year']:
        value = request.GET.get(field)
        if value:
            cars = cars.filter(**{field if field != 'brand' else 'brand__slug': value})

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        cars = cars.filter(price__gte=min_price)
    if max_price:
        cars = cars.filter(price__lte=max_price)

    paginator = Paginator(cars, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'cars/listing.html', {'page_obj': page_obj, 'brands': Brand.objects.all(), 'categories': Category.objects.all()})


def detail(request, pk):
    car = get_object_or_404(Car, pk=pk, is_approved=True)
    context = {
        'car': car,
        'inquiry_form': InquiryForm(),
        'booking_form': BookingForm(),
        'review_form': ReviewForm(),
    }
    return render(request, 'cars/detail.html', context)


@login_required
def create(request):
    form = CarForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        car = form.save(commit=False)
        car.seller = request.user
        car.save()
        messages.success(request, 'Listing created and awaiting admin approval.')
        return redirect('dashboard:my_listings')
    return render(request, 'cars/form.html', {'form': form, 'title': 'Add Car Listing'})


@login_required
def update(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if car.seller != request.user:
        return HttpResponseForbidden('Not allowed')
    form = CarForm(request.POST or None, request.FILES or None, instance=car)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Listing updated.')
        return redirect('dashboard:my_listings')
    return render(request, 'cars/form.html', {'form': form, 'title': 'Edit Listing'})


@login_required
def delete(request, pk):
    car = get_object_or_404(Car, pk=pk, seller=request.user)
    if request.method == 'POST':
        car.delete()
        messages.success(request, 'Listing deleted.')
    return redirect('dashboard:my_listings')


@login_required
def toggle_favourite(request, pk):
    car = get_object_or_404(Car, pk=pk, is_approved=True)
    fav, created = Favourite.objects.get_or_create(user=request.user, car=car)
    if not created:
        fav.delete()
        messages.info(request, 'Removed from saved cars.')
    else:
        messages.success(request, 'Saved to favourites.')
    return redirect('cars:detail', pk=pk)


@login_required
def send_inquiry(request, pk):
    car = get_object_or_404(Car, pk=pk, is_approved=True)
    form = InquiryForm(request.POST)
    if form.is_valid():
        inquiry = form.save(commit=False)
        inquiry.sender = request.user
        inquiry.car = car
        inquiry.save()
        messages.success(request, 'Inquiry sent to seller.')
    return redirect('cars:detail', pk=pk)


@login_required
def create_booking(request, pk):
    car = get_object_or_404(Car, pk=pk, is_approved=True)
    form = BookingForm(request.POST)
    if form.is_valid():
        booking = form.save(commit=False)
        booking.user = request.user
        booking.car = car
        booking.save()
        messages.success(request, 'Inspection booking created.')
    return redirect('cars:detail', pk=pk)
