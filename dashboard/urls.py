from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('saved/', views.saved_cars, name='saved_cars'),
    path('inquiries/', views.inquiries, name='inquiries'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
]
