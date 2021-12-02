from django.urls import path
from . import views

app_name = 'qr_labels'

urlpatterns = [
    path('', views.home, name='qr_home'),
]