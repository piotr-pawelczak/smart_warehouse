from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('warehouses/', views.warehouse_list, name='warehouses_list'),
    path('warehouse/<slug:slug>/', views.warehouse_detail, name='warehouse_detail'),
    path('warehouse/<slug:slug>/delete/', views.warehouse_delete, name='warehouse_delete'),
    path('shelf/<int:pk>/delete/', views.shelf_delete, name='shelf_delete'),
    path('shelf/<int:pk>/', views.shelf_detail, name='shelf_detail'),
    path('location/<int:pk>/', views.location_detail, name='location_detail'),
    path('products/', views.product_list, name='product_list'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/delete/<int:pk>', views.product_delete, name='product_delete'),
    path('product/edit/<int:pk>/', views.product_edit, name='product_edit'),
]