from django import forms
from documents.models import *
from warehouse.models import Warehouse, Shelf


class GoodsIssueForm(forms.ModelForm):
    class Meta:
        model = GoodsIssueNote
        fields = ['contractor', 'confirmed', 'warehouse']

    def __init__(self, *args, **kwargs):
        super(GoodsIssueForm, self).__init__(*args, **kwargs)
        self.fields['warehouse'].queryset = Warehouse.objects.filter(is_active=True)


class InternalGoodsIssueForm(forms.ModelForm):
    class Meta:
        model = InternalGoodsIssueNote
        fields = ['confirmed', 'warehouse']

    def __init__(self, *args, **kwargs):
        super(InternalGoodsIssueForm, self).__init__(*args, **kwargs)
        self.fields['warehouse'].queryset = Warehouse.objects.filter(is_active=True)


class GoodsReceivedForm(forms.ModelForm):

    class Meta:
        model = GoodsReceivedNote
        fields = ['contractor', 'confirmed', 'warehouse']

    def __init__(self, *args, **kwargs):
        super(GoodsReceivedForm, self).__init__(*args, **kwargs)
        self.fields['warehouse'].queryset = Warehouse.objects.filter(is_active=True)


class InternalGoodsReceivedForm(forms.ModelForm):

    class Meta:
        model = InternalGoodsReceivedNote
        fields = ['confirmed', 'warehouse']

    def __init__(self, *args, **kwargs):
        super(InternalGoodsReceivedForm, self).__init__(*args, **kwargs)
        self.fields['warehouse'].queryset = Warehouse.objects.filter(is_active=True)


class InterBranchTransferMinusForm(forms.ModelForm):

    class Meta:
        model = InterBranchTransferMinus
        fields = ['confirmed', 'warehouse', 'target_warehouse']


class ProductDocumentReceivedForm(forms.ModelForm):

    shelf = forms.ModelChoiceField(queryset=Shelf.objects.all())

    class Meta:
        model = ProductDocument
        fields = ['location', 'product', 'quantity', 'price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['shelf'].queryset = Shelf.objects.none()
        self.fields['location'].queryset = Location.objects.none()
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        self.fields['price'] = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0)

        if 'warehouse' in self.data:
            try:
                warehouse_id = int(self.data.get('warehouse'))
                self.fields['shelf'].queryset = Warehouse.objects.get(id=warehouse_id).shelves.filter(is_active=True)
            except (ValueError, TypeError):
                pass
        elif self.instance.id:
            self.fields['shelf'].queryset = self.instance.location.parent_shelf.warehouse.shelves.filter(is_active=True)
        elif self.is_bound:
            self.fields['shelf'].queryset = Shelf.objects.filter(is_active=True)

        if 'shelf' in self.data:
            try:
                shelf_id = int(self.data.get('shelf'))
                self.fields['location'].queryset = Shelf.objects.get(id=shelf_id).locations.filter(is_active=True)
            except (ValueError, TypeError):
                pass
        elif self.instance.id:
            self.fields['location'].queryset = self.instance.location.parent_shelf.locations.filter(is_active=True)

        if self.is_bound:
            self.fields['location'].queryset = Location.objects.filter(is_active=True)


class ProductDocumentIssueForm(forms.ModelForm):

    class Meta:
        model = ProductDocument
        fields = ['location', 'product', 'quantity', 'price', 'lot_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].queryset = Location.objects.none()
        self.fields['product'].queryset = Product.objects.none()

        if 'warehouse' in self.data:
            try:
                warehouse_id = int(self.data.get('warehouse'))
                self.fields['product'].queryset = Warehouse.objects.get(id=warehouse_id).get_available_products()
            except (ValueError, TypeError):
                pass
        elif self.instance.id:
            self.fields['product'].queryset = self.instance.location.parent_shelf.warehouse.get_available_products()

        if self.is_bound:
            self.fields['product'].queryset = Product.objects.filter(is_active=True)

        if 'product' in self.data:
            try:
                product_id = int(self.data.get('product'))
                warehouse_id = int(self.data.get('warehouse_product'))
                self.fields['location'].queryset = Product.objects.get(id=product_id).locations().filter(
                    location__parent_shelf__warehouse_id=warehouse_id, location__is_active=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.id:
            warehouse_id = self.instance.location.parent_shelf.warehouse.id
            self.fields['location'].queryset = self.instance.location.parent_shelf.locations.filter(is_active=True, parent_shelf__warehouse__id=warehouse_id, parent_shelf__is_active=True)
        if self.is_bound:
            self.fields['location'].queryset = Location.objects.all()


class ProductTransferForm(ProductDocumentIssueForm):
    class Meta:
        model = ProductTransfer
        exclude = ()
    
    def __init__(self, *args, **kwargs):
        super(ProductTransferForm, self).__init__(*args, **kwargs)
        self.fields['location_target'].queryset = Location.objects.none()

        if 'target-warehouse' in self.data:
            try:
                warehouse_id = int(self.data.get('target-warehouse'))
                self.fields['location_target'].queryset = Location.objects.filter(parent_shelf__warehouse_id=warehouse_id, is_active=True, parent_shelf__is_active=True)
            except (ValueError, TypeError):
                pass
        elif self.instance.id:
            warehouse_id = self.instance.location_target.parent_shelf.warehouse.id
            self.fields['location_target'].queryset = Location.objects.filter(parent_shelf__warehouse_id=warehouse_id, is_active=True, parent_shelf__is_active=True)

        if self.is_bound:
            self.fields['location_target'].queryset = Location.objects.filter(is_active=True)


class ContractorForm(forms.ModelForm):
    class Meta:
        model = Contractor
        exclude = ()
        labels = {'name': 'Nazwa', 'address': 'Adres', 'phone_number': 'Numer telefonu'}

    


