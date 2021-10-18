from django.contrib import admin
from .models import Warehouse, Shelf, Location, Product, ProductLocation

# Register your models here.


class ProductLocationInline(admin.TabularInline):
    model = ProductLocation
    raw_id_fields = ['product']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [ProductLocationInline]


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'city']


@admin.register(Shelf)
class RackAdmin(admin.ModelAdmin):
    list_display = ['name']
    ordering = ('name',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    inlines = [ProductLocationInline]
    ordering = ('name',)

