from django.contrib import admin

from .models import Booking, Brand, Car, CarImage, Category, Favourite, Inquiry, Review


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'price', 'seller', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'brand', 'fuel_type', 'transmission')
    search_fields = ('title', 'model', 'seller__username')
    actions = ['approve_listings']

    def approve_listings(self, request, queryset):
        queryset.update(is_approved=True)


admin.site.register([Category, Brand, CarImage, Favourite, Inquiry, Review, Booking])
