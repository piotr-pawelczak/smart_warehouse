from django.urls import path
from .views import *

app_name = 'api'
urlpatterns = [
    path('user/', UserRecordView.as_view(), name='users'),
    path('product/', ProductRecordView.as_view(), name='products'),
    path('product/<int:pk>', ProductDetail.as_view(), name='product_detail')
]