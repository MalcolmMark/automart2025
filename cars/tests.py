from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from cars.models import Brand, Car, Category, Favourite, Inquiry


class CarFeatureTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='seller', password='StrongPass123!')
        self.brand = Brand.objects.create(name='Toyota', slug='toyota')
        self.category = Category.objects.create(name='Sedan', slug='sedan')
        img = SimpleUploadedFile('car.jpg', b'file_content', content_type='image/jpeg')
        self.car = Car.objects.create(
            title='Toyota Camry', brand=self.brand, category=self.category, model='Camry', year=2020,
            price=20000, mileage=20000, fuel_type='petrol', transmission='automatic', color='Black',
            condition='used', description='Nice car', image=img, seller=self.user, location='Nairobi', is_approved=True
        )

    def test_search(self):
        response = self.client.get(reverse('cars:listing'), {'q': 'Camry'})
        self.assertContains(response, 'Toyota Camry')

    def test_favourite(self):
        buyer = User.objects.create_user(username='buyer', password='StrongPass123!')
        self.client.login(username='buyer', password='StrongPass123!')
        self.client.get(reverse('cars:favourite', kwargs={'pk': self.car.pk}))
        self.assertTrue(Favourite.objects.filter(user=buyer, car=self.car).exists())

    def test_contact_seller(self):
        buyer = User.objects.create_user(username='buyer2', password='StrongPass123!')
        self.client.login(username='buyer2', password='StrongPass123!')
        self.client.post(reverse('cars:inquiry', kwargs={'pk': self.car.pk}), {'message': 'Is price negotiable?'})
        self.assertTrue(Inquiry.objects.filter(sender=buyer, car=self.car).exists())
