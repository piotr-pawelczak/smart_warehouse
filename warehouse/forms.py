from django import forms
from warehouse.models import Warehouse, Shelf, Product


class WarehouseForm(forms.ModelForm):

    class Meta:
        model = Warehouse
        fields = ['name', 'symbol', 'city', 'address', 'description']

        # Usunięcie etykiet
        labels = {'name': '', 'symbol': '', 'city': '', 'address': '', 'description': ''}

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
        fields = ['shelf_number', 'columns', 'levels', 'zone']
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
