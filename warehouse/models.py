from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from custom_functions.accents import remove_accents
import datetime

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

    WAREHOUSE_TYPE_CHOICES = [
        ("storage", 'Przechowywanie'),
        ("receiving", 'Przyjmowanie'),
        ("shipping", 'Wysyłka')
    ]

    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=3, unique=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=100, blank=True, allow_unicode=True, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Funkcja zwracająca adres url magazynu potrzebny do widoku warehouse_detail
        :return: Adres url magazynu
        """
        return reverse('warehouse:warehouse_detail', args=[self.slug])

    def get_products(self):
        shelves = self.shelves.all()
        products = [shelf.get_products() for shelf in shelves]
        products_flat = [product for queryset in products for product in queryset]
        return products_flat

    def get_history(self):
        documents = self.documents.all()
        product_documents = [x.products.all() for x in documents if x.confirmed]
        products_flat = [product for queryset in product_documents for product in queryset]
        return products_flat

    @property
    def is_deletable(self):
        for shelf in self.shelves.all():
            if not shelf.is_deletable:
                return False
        return True

    def save(self, *args, **kwargs):
        self.slug = slugify(remove_accents(self.name))
        super(Warehouse, self).save(*args, **kwargs)


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

    SHELF_ZONE_CHOICES = [
        ("storage", 'Magazynowanie'),
        ("receiving", 'Przyjmowanie'),
        ("shipping", 'Wysyłka')
    ]

    warehouse = models.ForeignKey(Warehouse, related_name='shelves', on_delete=models.CASCADE)
    shelf_number = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    name = models.CharField(unique=True, max_length=50)
    columns = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    levels = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    zone = models.CharField(max_length=20, choices=SHELF_ZONE_CHOICES, default='storage')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Shelves"

    def get_absolute_url(self):
        return reverse('warehouse:shelf_detail', args=[self.pk])

    def get_products(self):
        products = [list(x.products.all()) for x in self.locations.all()]
        products_flat = [product for queryset in products for product in queryset]
        return products_flat

    @property
    def is_deletable(self):
        for location in self.locations.all():
            if not location.is_deletable:
                return False
        return True

    def save(self, *args, **kwargs):

        if self.zone == 'storage':
            zone_symbol = 'M'
        elif self.zone == 'receiving':
            zone_symbol = 'P'
        else:
            zone_symbol = 'W'

        self.name = f'{self.warehouse.symbol}-{zone_symbol}-{self.shelf_number}'
        super(Shelf, self).save(*args, **kwargs)


class Location(models.Model):
    name = models.CharField(max_length=200)
    parent_shelf = models.ForeignKey(Shelf, related_name='locations', on_delete=models.CASCADE)
    column_index = models.SmallIntegerField(default=1, validators=[MinValueValidator(1)])
    level_index = models.SmallIntegerField(default=1, validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)
    max_load = models.DecimalField(max_digits=12, decimal_places=3, default=100)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    @property
    def is_deletable(self):
        return not self.documents.exists()

    @property
    def get_current_load(self):
        products = self.products.all()
        current_load = 0
        for productlocation in products:
            weight = productlocation.product.weight
            quantity = productlocation.quantity
            current_load += weight * quantity
        return current_load

    def save(self, *args, **kwargs):
        self.name = f'{self.parent_shelf.name}-{self.column_index}-{self.level_index}'
        super(Location, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('warehouse:location_detail', args=[self.id])


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=100, blank=True, allow_unicode=True, unique=True)
    sku = models.CharField(max_length=10, unique=True, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=3)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    @property
    def total_quantity(self):
        quantity = 0
        for q in self.locations.all():
            quantity += q.quantity
        return quantity

    @property
    def is_deletable(self):
        return not self.documents.exists()

    def __str__(self):
        return f'{self.name} [{self.sku}]'

    def get_absolute_url(self):
        return reverse('warehouse:product_detail', args=[self.pk, self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(remove_accents(self.name))
        super(Product, self).save(*args, **kwargs)


class ProductLocation(models.Model):
    product = models.ForeignKey(Product, related_name='locations', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, related_name='products', on_delete=models.CASCADE)
    lot_number = models.CharField(default=datetime.datetime.now().strftime("%d/%m/%Y"), max_length=10)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.id}"