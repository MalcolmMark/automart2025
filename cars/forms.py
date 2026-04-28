from django import forms

from .models import Booking, Car, CarImage, Inquiry, Review


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        exclude = ('seller', 'is_approved')


class CarImageForm(forms.ModelForm):
    class Meta:
        model = CarImage
        fields = ('image',)


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ('message',)


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('inspection_date', 'notes')


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'comment')
