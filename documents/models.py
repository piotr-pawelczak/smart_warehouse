from django.contrib.auth.models import User
from django.db import models
from polymorphic.models import PolymorphicModel
from warehouse.models import Product, Location, Warehouse, ProductLocation
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField


class Contractor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=100)
    phone_number = PhoneNumberField(null=False, blank=False)
    email = models.EmailField(max_length=50)

    phone_number.error_messages['invalid'] = 'Podaj poprawny numer telefonu. Użyj kodu krajowego np (+48)'

    def __str__(self):
        return self.name

    def formatted_phone(self, country='PL'):
        string = str(self.phone_number)
        length = 3
        return ' '.join(string[i:i+length] for i in range(0, len(string), length))


class Document(PolymorphicModel):
    document_number = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='documents')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.document_number

    def get_absolute_url(self):
        return reverse('documents:detail', args=[self.id])

    def get_value(self):
        value = 0
        for document_product in self.products.all():
            value += document_product.calculate_value()
        return value

    @property
    def get_source_warehouse(self):
        if InterBranchTransferPlus.objects.get(id=self.id):
            return InterBranchTransferPlus.objects.get(id=self.id).source_warehouse
        elif InterBranchTransferMinus.objects.get(id=self.id):
            return InterBranchTransferMinus.objects.get(id=self.id).warehouse
        else:
            return None

    @property
    def get_target_warehouse(self):
        if InterBranchTransferPlus.objects.get(id=self.id):
            return InterBranchTransferPlus.objects.get(id=self.id).warehouse
        elif InterBranchTransferMinus.objects.get(id=self.id):
            return InterBranchTransferMinus.objects.get(id=self.id).target_warehouse
        else:
            return None


class GoodsReceivedNote(Document):
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True)
    document_type = models.CharField(default='PZ', max_length=3)


class InternalGoodsReceivedNote(Document):
    document_type = models.CharField(default='PW', max_length=3)


class GoodsIssueNote(Document):
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True)
    document_type = models.CharField(default='WZ', max_length=3)


class InternalGoodsIssueNote(Document):
    document_type = models.CharField(default='RW', max_length=3)


class InterBranchTransferMinus(Document):
    target_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    document_type = models.CharField(default='MM-', max_length=3)


class InterBranchTransferPlus(Document):
    source_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    document_type = models.CharField(default='MM+', max_length=3)


class ProductDocument(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='documents')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='documents')
    quantity = models.PositiveIntegerField()
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    lot_number = models.CharField(null=True, blank=True, max_length=20)

    @property
    def type(self):
        return self.document.document_type

    def calculate_value(self):
        return self.quantity * self.price

    @property
    def target_location(self):
        if ProductTransfer.objects.get(id=self.id):
            return ProductTransfer.objects.get(id=self.id).location_target
        else:
            return None


class ProductTransfer(ProductDocument):
    location_target = models.ForeignKey(Location, on_delete=models.CASCADE)
