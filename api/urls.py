from django.urls import path
from .views import *

app_name = 'api'
urlpatterns = [
    path('user/', UserRecordView.as_view(), name='users'),
    path('product/', ProductRecordView.as_view(), name='products'),
    path('product/<int:pk>', ProductDetail.as_view(), name='product_detail'),
    path('product-location', ProductLocationRecordView.as_view(), name='product_locations'),
    path('product-location-detail/', ProductLocationDetail.as_view(), name='product_location_detail'),
    path('product-location-update/<int:pk>', ProductLocationUpdate.as_view(), name='product_location_update'),
    path('product-location-create/', ProductLocationCreate.as_view(), name='product_location_create'),
]