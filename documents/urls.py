from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    #path('', views.goods_issue_create, name='document_create'),
    path('', views.DocumentListView.as_view(), name='list'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='detail'),
    path('pz/', views.goods_received_create, name='goods_received_create'),
    path('ajax/load-product-locations/', views.load_product_locations, name='ajax_load_product_locations'),
    path('ajax/load-shelves/', views.load_shelves, name='ajax_load_shelves'),
    path('ajax/load-locations/', views.load_locations, name='ajax_load_locations'),
    path('pz/update', views.goods_received_notes_update, name='goods_received_update'),
    path('contractors', views.contractors_list, name='contractors'),
    path('contractor/<int:pk>/delete', views.contractor_delete, name='contractor-delete'),
    path('contractor/<int:pk>/update', views.contractor_update, name='contractor-update'),
]