from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Car(models.Model):
    FUEL_CHOICES = [('petrol', 'Petrol'), ('diesel', 'Diesel'), ('hybrid', 'Hybrid'), ('electric', 'Electric')]
    TRANSMISSION_CHOICES = [('automatic', 'Automatic'), ('manual', 'Manual')]
    CONDITION_CHOICES = [('new', 'New'), ('used', 'Used')]

    title = models.CharField(max_length=180)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='cars')
    model = models.CharField(max_length=120)
    year = models.PositiveIntegerField(validators=[MinValueValidator(1980), MaxValueValidator(timezone.now().year + 1)])
    price = models.DecimalField(max_digits=12, decimal_places=2)
    mileage = models.PositiveIntegerField(default=0)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    color = models.CharField(max_length=60)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    description = models.TextField()
    image = models.ImageField(upload_to='cars/main/')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cars')
    location = models.CharField(max_length=120)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('cars:detail', kwargs={'pk': self.pk})


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='cars/gallery/')


class Favourite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favourites')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='favourited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'car')


class Inquiry(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='inquiries')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Booking(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')]
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    inspection_date = models.DateField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
