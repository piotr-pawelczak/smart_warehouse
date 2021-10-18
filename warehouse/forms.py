from django import forms
from warehouse.models import Warehouse, Shelf
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit


class WarehouseForm(forms.ModelForm):

    class Meta:
        model = Warehouse
        fields = ['name', 'symbol', 'city', 'address']

        # Usunięcie etykiet
        labels = {'name': '', 'symbol': '', 'city': '', 'address': ''}

        # Ustawienie wartości wyświetlających się na polach formularza
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nazwa magazynu'}),
            'symbol': forms.TextInput(attrs={'placeholder': 'Symbol (maksymalnie 3 znaki)'}),
            'city': forms.TextInput(attrs={'placeholder': 'Miasto'}),
            'address': forms.TextInput(attrs={'placeholder': 'Adres'})
        }


class ShelfForm(forms.ModelForm):
    class Meta:
        model = Shelf
        fields = ['name', 'rows', 'cols']