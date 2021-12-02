from django import forms
from warehouse.models import Warehouse, Shelf, Product, Location


class WarehouseQrForm(forms.Form):
    warehouse = forms.ModelChoiceField(Warehouse.objects.all())


class ShelfQrForm(forms.Form):
    shelf = forms.ModelChoiceField(Shelf.objects.all())


class LocationQrForm(forms.Form):
    location = forms.ModelChoiceField(Location.objects.all())
