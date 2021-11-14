from django.contrib import admin
from django.urls import path, include
from ajax_select import urls as ajax_select_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('warehouse.urls')),
    path('document/', include('documents.urls')),
    path('ajax_select', include(ajax_select_urls)),
]
