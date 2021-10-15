from django.db import models


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(default=0)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_quantity(self):
        quantity = 0
        for q in self.locations.all():
            quantity += q.quantity
        self.quantity = quantity


class Location(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class ProductLocation(models.Model):
    product = models.ForeignKey(Product, related_name='locations', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, related_name='products', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.id}"
