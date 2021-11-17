from django.db import models
from polymorphic.models import PolymorphicModel
from warehouse.models import Product, Location
from django.urls import reverse

class Contractor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Document(PolymorphicModel):
    document_number = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.document_number

    def get_absolute_url(self):
        return reverse('documents:detail', args=[self.id])


class GoodsReceivedNote(Document):
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    document_type = models.CharField(default='GRN', max_length=3)


class GoodsIssueNote(Document):
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)


class InternalGoodsIssueNote(Document):
    warehouse = models.CharField(max_length=60)


class ProductDocument(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='documents')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=12, decimal_places=2)
