from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    #path('', views.goods_issue_create, name='document_create'),

    # General documents urls
    path('', views.DocumentListView.as_view(), name='list'),
    path('<int:pk>/', views.document_detail, name='detail'),
    path('delete/<int:pk>/', views.document_delete, name='document-delete'),

    # Create document urls
    path('received/<str:document_type>/', views.goods_received_create, name='goods_received_create'),
    path('issue/<str:document_type>/', views.goods_issue_create, name='goods_issue_create'),
    path('transfer/mm/', views.interbranch_transfer_create, name='interbranch_transfer_create'),

    # Update document urls
    path('received/update/<str:document_type>/<int:pk>/', views.goods_received_notes_update, name='goods_received_update'),
    path('issue/update/<str:document_type>/<int:pk>/', views.goods_issue_update, name='goods_issue_update'),
    path('transfer/update/mm/<int:pk>/', views.interbranch_transfer_update, name='interbranch_transfer_update'),

    # Contractors urls
    path('contractors/', views.contractors_list, name='contractors'),
    path('contractor/<int:pk>/delete/', views.contractor_delete, name='contractor-delete'),
    path('contractor/<int:pk>/update/', views.contractor_update, name='contractor-update'),

    # AJAX update form urls
    path('ajax/load-product-locations/', views.load_product_locations, name='ajax_load_product_locations'),
    path('ajax/load-shelves/', views.load_shelves, name='ajax_load_shelves'),
    path('ajax/load-locations/', views.load_locations, name='ajax_load_locations'),
    path('ajax/load-warehouse-products/', views.load_warehouse_products, name='ajax_load_warehouse_products'),
    path('ajax/load-target-locations/', views.load_target_locations, name='ajax_load_target_locations'),
]
