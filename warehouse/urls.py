from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('warehouses/', views.warehouse_list, name='warehouses_list'),
    path('warehouse/<int:pk>/', views.warehouse_detail, name='warehouse_detail'),
    path('warehouse/<int:pk>/delete', views.warehouse_delete, name='warehouse_delete'),
    path('shelf/<int:pk>/delete', views.shelf_delete, name='shelf_delete'),
    # path('warehouse/<int:pk>/edit', views.warehouse_edit, name='warehouse_edit'),
]