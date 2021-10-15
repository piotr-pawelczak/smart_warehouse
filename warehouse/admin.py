from django.contrib import admin
from .models import Product, Location, ProductLocation

# Register your models here.


class ProductLocationInline(admin.TabularInline):
    model = ProductLocation
    raw_id_fields = ['product']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [ProductLocationInline]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    inlines = [ProductLocationInline]

