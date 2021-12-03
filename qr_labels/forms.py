from django import forms
from warehouse.models import Warehouse, Shelf, Product, Location, ProductLocation


class WarehouseQrForm(forms.Form):
    warehouse = forms.ModelChoiceField(Warehouse.objects.all())


class ShelfQrForm(forms.Form):
    shelf = forms.ModelChoiceField(Shelf.objects.all())


class LocationQrForm(forms.Form):
    location = forms.ModelChoiceField(Location.objects.all())


class ProductQrForm(forms.Form):
    product = forms.ModelChoiceField(Product.objects.all())
    location = forms.ModelChoiceField(Location.objects.all())
    quantity = forms.IntegerField(min_value=1)
    lot_number = forms.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["location"].queryset = Location.objects.none()

        if self.is_bound:
            self.fields["location"].queryset = Location.objects.all()
