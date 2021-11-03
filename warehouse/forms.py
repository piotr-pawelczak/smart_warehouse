from django import forms
from warehouse.models import Warehouse, Shelf, Product


class WarehouseForm(forms.ModelForm):

    class Meta:
        model = Warehouse
        fields = ['name', 'symbol', 'city', 'address', 'description', 'type']

        # Usunięcie etykiet
        labels = {'name': '', 'symbol': '', 'city': '', 'address': '', 'description': '', 'type': 'Funkcja magazynu'}

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
        fields = ['shelf_number', 'columns', 'levels']
        labels = {'shelf_number': 'Numer regału', 'columns': 'Liczba kolumn', 'levels': 'Liczba poziomów'}


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'unit', 'description', 'sku', 'weight']
        labels = {'name': 'Nazwa produktu', 'unit': 'Jednostka', 'description': 'Opis', 'sku': 'SKU', 'weight': 'Waga [kg]'}
