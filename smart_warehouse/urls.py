from django.contrib import admin
from django.urls import path, include
from ajax_select import urls as ajax_select_urls
from rest_framework.authtoken import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('warehouse.urls')),
    path('document/', include('documents.urls')),
    path('account/', include('account.urls')),
    path('ajax_select', include(ajax_select_urls)),
    path('qr/', include('qr_labels.urls')),
    path('api/', include('api.urls', namespace='api')),
    path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
]
