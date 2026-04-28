from django.urls import path

from . import views

app_name = 'cars'

urlpatterns = [
    path('', views.listing, name='listing'),
    path('add/', views.create, name='create'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/edit/', views.update, name='update'),
    path('<int:pk>/delete/', views.delete, name='delete'),
    path('<int:pk>/favourite/', views.toggle_favourite, name='favourite'),
    path('<int:pk>/inquiry/', views.send_inquiry, name='inquiry'),
    path('<int:pk>/booking/', views.create_booking, name='booking'),
]
