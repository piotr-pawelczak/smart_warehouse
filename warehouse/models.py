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
        return reverse('warehouse:warehouse_detail', args=[self.pk])


class Shelf(models.Model):
    """
    Model reprezentujący regał. Pola modelu oznaczają:
    *warehouse: magazyn, do którego należy regał
    *shelf_number: numer regału
    *name: nazwa regału, generowana automatycznie jako symbol_magazynu-numer_regalu
    *columns: liczba kolumn
    *levels: liczba poziomów

    shelf.locations.all() zwraca wszystkie lokalizacje powiązane z regałem
    """
    warehouse = models.ForeignKey(Warehouse, related_name='shelves', on_delete=models.CASCADE)
    shelf_number = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    name = models.CharField(unique=True, max_length=50)
    columns = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    levels = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Shelves"

    def get_absolute_url(self):
        return reverse('warehouse:shelf_detail', args=[self.pk])


class Location(models.Model):
    name = models.CharField(max_length=200)
    parent_shelf = models.ForeignKey(Shelf, related_name='locations', on_delete=models.CASCADE)
    column_index = models.SmallIntegerField(default=1, validators=[MinValueValidator(1)])
    level_index = models.SmallIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        ordering = ('name',)

    # @property
    # def column_index(self):
    #     name_list = self.name.split('-')
    #     return name_list[1]
    #
    # @property
    # def level_index(self):
    #     name_list = self.name.split('-')
    #     return name_list[2]

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
