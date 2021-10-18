from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator

# Create your models here.


class Warehouse(models.Model):
    """
    Model reprezentujący magazyn. Pola modelu oznaczają:
    * name: nazwa magazynu
    * symbol: symbol magazynu używany przy oznaczeniach lokalizacji (maksymalnie 3 znaki)
    * city: miasto, w którym magazyn się znajduje
    * address: reszta adresu magazynu (ulica, numer)
    * description: opcjonalny opis magazynu

    Hierarchia lokalizacji:
    Warehouse > Shelf > Location
    warehouse.shelves.all() zwraca wszystkie
    """
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=3, unique=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Funkcja zwracająca adres url magazynu potrzebny do widoku warehouse_detail
        :return: Adres url magazynu
        """
        return reverse('warehouse:warehouse_detail', args=[self.id])


class Shelf(models.Model):
    warehouse = models.ForeignKey(Warehouse, related_name='shelves', on_delete=models.CASCADE)
    name = models.CharField(unique=True, max_length=50)
    columns = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    levels = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Shelves"


class Location(models.Model):
    name = models.CharField(max_length=200)
    parent_shelf = models.ForeignKey(Shelf, related_name='locations', on_delete=models.CASCADE)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    @property
    def total_quantity(self):
        quantity = 0
        for q in self.locations.all():
            quantity += q.quantity
        return quantity


class ProductLocation(models.Model):
    product = models.ForeignKey(Product, related_name='locations', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, related_name='products', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.id}"
