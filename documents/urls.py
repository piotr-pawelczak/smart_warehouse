from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.goods_issue_create, name='document_create'),
    path('pz/', views.goods_received_create, name='goods_received_create'),
    path('ajax/load-product-locations/', views.load_product_locations, name='ajax_load_product_locations'),
    path('ajax/load-shelves/', views.load_shelves, name='ajax_load_shelves'),
    path('ajax/load-locations/', views.load_locations, name='ajax_load_locations'),
    path('pz/update', views.goods_received_notes_update, name='goods_received_update'),
]