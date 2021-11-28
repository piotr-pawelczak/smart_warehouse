from django import forms
from warehouse.models import Warehouse, Shelf, Product, Location


class WarehouseForm(forms.ModelForm):

    class Meta:
        model = Warehouse
        fields = ['name', 'symbol', 'city', 'address', 'description', 'is_active']

        # Usunięcie etykiet
        labels = {'name': '', 'symbol': '', 'city': '', 'address': '', 'description': '', 'is_active': ''}

        # Ustawienie wartości wyświetlających się na polach formularza
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nazwa magazynu'}),
            'symbol': forms.TextInput(attrs={'placeholder': 'Symbol (maksymalnie 3 znaki)'}),
            'city': forms.TextInput(attrs={'placeholder': 'Miasto'}),
            'address': forms.TextInput(attrs={'placeholder': 'Adres'}),
            'description': forms.Textarea(attrs={'placeholder': 'Opis'}),
        }


class ShelfForm(forms.ModelForm):
    class Meta:
        model = Shelf
        fields = ['shelf_number', 'columns', 'levels', 'zone', 'is_active']
        labels = {'shelf_number': 'Numer regału', 'columns': 'Liczba kolumn', 'levels': 'Liczba poziomów', 'zone': 'Strefa'}

    def clean(self):
        number = self.cleaned_data['shelf_number']
        zone = self.cleaned_data['zone']

        if self.instance.shelf_number != number or self.instance.zone != zone:
            if Shelf.objects.filter(zone=zone, shelf_number=number).exists():
                raise forms.ValidationError('Istnieje już regał o tym numerze w wybranej strefie')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description',  'weight', 'is_active']
        labels = {'name': 'Nazwa produktu', 'description': 'Opis', 'weight': 'Waga [kg]', 'is_active': ''}


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['max_load', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['max_load'] = forms.DecimalField(max_digits=12, decimal_places=3, min_value=0)


class LoadLocationForm(forms.Form):
    max_load = forms.DecimalField(max_digits=12, decimal_places=3, min_value=0)
