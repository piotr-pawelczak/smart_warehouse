from django.urls import path
from . import views

app_name = 'qr_labels'

urlpatterns = [
    path('location/', views.generate_location_labels, name='generate_locations'),
    path('product/', views.generate_product_labels, name='generate_products'),
]