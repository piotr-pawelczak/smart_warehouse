from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Warehouse, Location, Shelf, Product
from django.shortcuts import get_object_or_404
from .forms import WarehouseForm, ShelfForm, ProductForm, LocationForm, LoadLocationForm
from django.contrib import messages
from django.urls import reverse
import copy


def home_view(request):
    return render(request, 'warehouse/base.html')


@login_required
def warehouse_list(request):
    """
    Widok do obsługi listy wszystkich magazynów
    Wyświetla listę magazynów oraz zawiera formularz do utworzenia nowego magazynu
    """
    warehouses = Warehouse.objects.all()

    # Obsługa formularza do utworzenia magazynu
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pomyślnie dodano nowy magazyn!')
            return redirect(reverse('warehouse:warehouses_list'))
    else:
        form = WarehouseForm()

    return render(request, 'warehouse/locations/warehouse_list.html', {'warehouses': warehouses, 'form': form})


@login_required
def warehouse_detail(request, slug):
    """
    Widok do obsługi pojedynczego magazynu
    Magazyn jest pobierany poprzez slug
    Zawiera informacje dotyczące magazynu, pozwala na modyfikacje magazynu
    Z poziomu tego widoku można dodawać regały
    """

    warehouse = get_object_or_404(Warehouse, slug=slug)
    shelves = warehouse.shelves.all().order_by('name')

    shelves_receiving = warehouse.shelves.filter(zone='receiving').order_by('shelf_number').all()
    shelves_storage = warehouse.shelves.filter(zone='storage').order_by('shelf_number').all()
    shelves_shipping = warehouse.shelves.filter(zone='shipping').order_by('shelf_number').all()

    # Formularz do edycji magazynu
    edit_form = WarehouseForm(instance=warehouse)
    if request.method == 'POST' and 'edit_warehouse_button' in request.POST:
        edit_form = WarehouseForm(request.POST, instance=warehouse)
        if edit_form.is_valid():
            edit_form.save()
            return redirect(warehouse.get_absolute_url())

    # Formularz do utworzenia regału
    if request.method == 'POST' and 'create_shelf_button' in request.POST:
        form = ShelfForm(request.POST)

        if form.is_valid():
            shelf = form.save(commit=False)
            cols = form.cleaned_data['columns']
            rows = form.cleaned_data['levels']
            shelf.warehouse = warehouse
            shelf.save()
            messages.success(request, 'Pomyślnie dodano nowy regał')

            # Utworzenie lokalizacji
            for lev in range(rows):
                for col in range(cols):
                    location_name = f'{shelf.name}-{col + 1}-{lev + 1}'
                    Location.objects.create(name=location_name, parent_shelf=shelf, level_index=lev + 1,
                                            column_index=col + 1)

    else:
        form = ShelfForm()

    context = {'warehouse': warehouse, 'form': form, 'shelves': shelves, 'edit_form': edit_form,
               'shelves_receiving': shelves_receiving, 'shelves_storage': shelves_storage,
               'shelves_shipping': shelves_shipping
               }
    return render(request, 'warehouse/locations/warehouse_detail.html', context)


@login_required
def warehouse_delete(request, pk):
    """
    Widok odpowiedzialny za usuwanie magazynu. Zostaje przekierowany do listy magazynów
    """
    warehouse = get_object_or_404(Warehouse, id=pk)
    if request.method == 'POST':
        warehouse.delete()
        messages.warning(request, 'Magazyn został usunięty')
    return redirect(reverse('warehouse:warehouses_list'))


@login_required
def shelf_detail(request, pk):
    shelf = get_object_or_404(Shelf, id=pk)
    locations = shelf.locations.all()

    # Zamiana listy obiektów na tablicę
    n = shelf.levels
    table = list(locations)
    table_2d = [table[i:i + n] for i in range(0, len(table), n)]
    locations_table = list(map(list, zip(*table_2d)))
    locations_table.reverse()

    # Formularz edycji nośności
    if request.method == 'POST' and 'load-location' in request.POST:
        load_form = LoadLocationForm(request.POST)
        if load_form.is_valid():
            max_load = load_form.cleaned_data['max_load']
            for location in locations:
                location.max_load = max_load
                location.save()
    else:
        load_form = LoadLocationForm()

    # Formularz do edycji regału
    edit_form = ShelfForm(instance=shelf)
    if request.method == 'POST' and 'shelf-edit' in request.POST:
        old_shelf = copy.copy(shelf)
        edit_form = ShelfForm(request.POST, instance=shelf)
        if edit_form.is_valid():
            columns = edit_form.cleaned_data['columns']
            levels = edit_form.cleaned_data['levels']
            new_shelf = edit_form.save(commit=False)

            # Zmiana nazw lokalizacji przy zmianie nazwy regału
            if new_shelf.name != old_shelf.name:
                for location in locations:
                    location.save()

            # Regeneracja lokalizacji
            locations_to_delete = []
            for elem in shelf.locations.filter(column_index__gt=columns):
                locations_to_delete.append(elem)
            for elem in shelf.locations.filter(level_index__gt=levels):
                locations_to_delete.append(elem)

            if any([not x.is_deletable for x in locations_to_delete]):
                messages.error(request, 'Nie można usunąć lokalizacji, z którą jest powiązany dokument')
                return redirect(shelf.get_absolute_url())
            else:
                new_shelf.save()
                for elem in locations_to_delete:
                    elem.delete()

                for lev in range(levels):
                    for col in range(columns):
                        location_name = f'{shelf.name}-{col + 1}-{lev + 1}'
                        # Jeżeli lokalizacja jest nowa
                        if not Location.objects.filter(name=location_name):
                            Location.objects.create(name=location_name, parent_shelf=shelf, level_index=lev + 1,
                                                    column_index=col + 1)

            return redirect(shelf.get_absolute_url())
        else:
            messages.error(request, 'Nie udało się zaktualizować regału. Sprawdź, czy numer regału nie jest zajęty.')

    context = {'shelf': shelf, 'locations': locations, 'locations_table': locations_table, 'edit_form': edit_form, 'load_form': load_form}
    return render(request, 'warehouse/locations/shelf_detail.html', context)


@login_required
def shelf_delete(request, pk):
    shelf = get_object_or_404(Shelf, id=pk)

    finish_url = shelf.warehouse.get_absolute_url()
    if request.method == 'POST':
        shelf.delete()
    return redirect(finish_url)


@login_required
def location_detail(request, pk):
    location = get_object_or_404(Location, id=pk)
    edit_form = LocationForm(instance=location)

    if request.method == 'POST':
        edit_form = LocationForm(request.POST, instance=location)
        if edit_form.is_valid():
            edit_form.save()
            return redirect(location.get_absolute_url())

    context = {'location': location, 'edit_form': edit_form}
    return render(request, 'warehouse/locations/location_detail.html', context)


@login_required
def product_list(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'warehouse/products/product_list.html', context)


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            new_product = form.save()

            sku_length = 5
            zeros_num = sku_length - len(str(new_product.id))
            new_product.sku = f'P{zeros_num * "0"}{new_product.id}'
            new_product.save()

            messages.success(request, 'Pomyślnie dodano nowy produkt!')
            return redirect(reverse('warehouse:product_list'))
    else:
        form = ProductForm()

    context = {'form': form}
    return render(request, 'warehouse/products/product_create.html', context)


@login_required
def product_detail(request, pk, slug):
    product = get_object_or_404(Product, id=pk)
    context = {'product': product}
    return render(request, 'warehouse/products/product_detail.html', context)


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, id=pk)
    if request.method == 'POST':
        product.delete()
        messages.warning(request, 'Produkt został usunięty')
    return redirect(reverse('warehouse:product_list'))


@login_required
def product_edit(request, pk):
    product = Product.objects.get(id=pk)

    edit_form = ProductForm(instance=product)
    if request.method == 'POST':
        edit_form = ProductForm(request.POST, instance=product)
        if edit_form.is_valid():
            edit_form.save()
            return redirect(product.get_absolute_url())
    context = {'edit_form': edit_form}

    return render(request, 'warehouse/products/product_edit.html', context)


@login_required
def warehouse_products(request, slug):
    warehouse = Warehouse.objects.get(slug=slug)
    context = {'warehouse': warehouse}
    return render(request, 'warehouse/locations/warehouse_products.html', context)


@login_required
def warehouse_documents(request, slug):
    warehouse = Warehouse.objects.get(slug=slug)
    context = {'warehouse': warehouse}
    return render(request, 'warehouse/locations/warehouse_documents.html', context)


@login_required
def warehouse_history(request, slug):
    warehouse = Warehouse.objects.get(slug=slug)
    received_type = ['PZ', 'PW', 'MM+']
    shipped_type = ['WZ', 'WW', 'MM-']

    context = {'warehouse': warehouse, 'received_type': received_type, 'shipped_type': shipped_type}
    return render(request, 'warehouse/locations/warehouse_history.html', context)
