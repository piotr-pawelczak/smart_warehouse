from django import forms
from documents.models import *
from warehouse.models import Warehouse, Shelf


class GoodsIssueForm(forms.ModelForm):
    class Meta:
        model = GoodsIssueNote
        fields = ['document_number', 'contractor']


class GoodsReceivedForm(forms.ModelForm):

    class Meta:
        model = GoodsReceivedNote
        fields = ['contractor', 'confirmed', 'warehouse']


class ProductDocumentReceivedForm(forms.ModelForm):

    shelf = forms.ModelChoiceField(queryset=Shelf.objects.all())

    class Meta:
        model = ProductDocument
        fields = ['location', 'product', 'quantity', 'price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['shelf'].queryset = Shelf.objects.none()
        self.fields['location'].queryset = Location.objects.none()
        self.empty_permitted = False

        if 'warehouse' in self.data:
            try:
                warehouse_id = int(self.data.get('warehouse'))
                self.fields['shelf'].queryset = Warehouse.objects.get(id=warehouse_id).shelves.all()
            except (ValueError, TypeError):
                pass
        elif self.instance.id:
            self.fields['shelf'].queryset = self.instance.location.parent_shelf.warehouse.shelves.all()
        elif self.is_bound:
            self.fields['shelf'].queryset = Shelf.objects.all()

        if 'shelf' in self.data:
            try:
                shelf_id = int(self.data.get('shelf'))
                self.fields['location'].queryset = Shelf.objects.get(id=shelf_id).locations.all()
            except (ValueError, TypeError):
                pass
        elif self.instance.id:
            print('Instance')
            self.fields['location'].queryset = self.instance.location.parent_shelf.locations.all()

        if self.is_bound:
            self.fields['location'].queryset = Location.objects.all()


class ProductDocumentForm(forms.ModelForm):

    class Meta:
        model = ProductDocument
        fields = ['product', 'location', 'quantity', 'price']

    def __init__(self, document_type, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if document_type in ['GIN', 'Internal GIN']:
            self.fields['location'].queryset = Location.objects.none()
            if 'product' in self.data:
                try:
                    product_id = int(self.data.get('product'))
                    self.fields['location'].queryset = [elem.location for elem in Product.objects.get(id=product_id).locations.filter(id=product_id)]
                except (ValueError, TypeError):
                    pass
            elif self.instance.id:
                self.fields['location'].queryset = [elem.location for elem in self.instance.product.locations.all()]
        else:
            self.fields['location'].queryset = Location.objects.all()


