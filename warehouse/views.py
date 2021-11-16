from django.shortcuts import render, redirect
from .models import Warehouse, Location, Shelf, Product
from django.shortcuts import get_object_or_404
from .forms import WarehouseForm, ShelfForm, ProductForm
from django.contrib import messages
from django.urls import reverse
import copy


def home_view(request):
    return render(request, 'warehouse/base.html')


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


def warehouse_detail(request, slug):
    """
    Widok do obsługi pojedynczego magazynu
    Magazyn jest pobierany poprzez slug
    Zawiera informacje dotyczące magazynu, pozwala na modyfikacje magazynu
    Z poziomu tego widoku można dodawać regały
    """

    warehouse = get_object_or_404(Warehouse, slug=slug)
    shelves = warehouse.shelves.all().order_by('name')

    # Automatyczna sugestia numeru nowego regału
    if shelves.count() == 0:
        default_number = 1
    else:
        default_number = shelves.reverse()[0].shelf_number + 1

    # Formularz do edycji magazynu
    edit_form = WarehouseForm(instance=warehouse)
    if request.method == 'POST' and 'edit_warehouse_button' in request.POST:
        edit_form = WarehouseForm(request.POST, instance=warehouse)
        if edit_form.is_valid():
            edit_form.save()
            return redirect(warehouse.get_absolute_url())

    # Formularz do utworzenia regału
    if request.method == 'POST' and 'create_shelf_button' in request.POST:
        form = ShelfForm(request.POST, initial={'shelf_number': default_number})
        if form.is_valid():
            shelf = form.save(commit=False)
            cols = form.cleaned_data['columns']
            rows = form.cleaned_data['levels']
            shelf.warehouse = warehouse
            shelf_name = f'{warehouse.symbol}-{shelf.shelf_number}'

            # Obsługa tej samej nazwy
            if Shelf.objects.filter(name=shelf_name):
                messages.error(request, 'Istnieje już regał o podanym numerze')
                return redirect(warehouse.get_absolute_url())

            shelf.name = f'{warehouse.symbol}-{shelf.shelf_number}'
            shelf.save()
            messages.success(request, 'Pomyślnie dodano nowy regał')

            default_number = shelves.reverse()[0].shelf_number + 1
            form = ShelfForm(initial={'shelf_number': default_number})

            # Utworzenie lokalizacji
            for lev in range(rows):
                for col in range(cols):
                    location_name = f'{shelf.name}-{col+1}-{lev+1}'
                    Location.objects.create(name=location_name, parent_shelf=shelf, level_index=lev+1, column_index=col+1)

    else:
        form = ShelfForm(initial={'shelf_number': default_number})

    context = {'warehouse': warehouse, 'form': form, 'shelves': shelves, 'edit_form': edit_form}
    return render(request, 'warehouse/locations/warehouse_detail.html', context)


def warehouse_delete(request, slug):
    """
    Widok odpowiedzialny za usuwanie magazynu. Zostaje przekierowany do listy magazynów
    """
    warehouse = get_object_or_404(Warehouse, slug=slug)
    if request.method == 'POST':
        warehouse.delete()
        messages.warning(request, 'Magazyn został usunięty')
    return redirect(reverse('warehouse:warehouses_list'))


def shelf_detail(request, pk):
    shelf = get_object_or_404(Shelf, id=pk)
    locations = shelf.locations.all()

    # Zamiana listy obiektów na tablicę
    n = shelf.levels
    table = list(locations)
    table_2d = [table[i:i+n] for i in range(0, len(table), n)]
    locations_table = list(map(list, zip(*table_2d)))
    locations_table.reverse()

    # Formularz do edycji regału
    edit_form = ShelfForm(instance=shelf)
    if request.method == 'POST':
        old_shelf = copy.copy(shelf)
        edit_form = ShelfForm(request.POST, instance=shelf)
        if edit_form.is_valid():
            columns = edit_form.cleaned_data['columns']
            levels = edit_form.cleaned_data['levels']
            shelf_number = edit_form.cleaned_data['shelf_number']
            new_shelf = edit_form.save(commit=False)

            # Obsługa tej samej nazwy
            if shelf_number != old_shelf.shelf_number:
                if Shelf.objects.filter(warehouse=shelf.warehouse, shelf_number=shelf_number):
                    messages.error(request, 'Istnieje już regał o podanym numerze')
                    return redirect(shelf.get_absolute_url())
                else:
                    for location in shelf.locations.all():
                        location.save()
            new_shelf.save()

            # Regeneracja lokalizacji
            for lev in range(levels):
                for col in range(columns):
                    location_name = f'{shelf.name}-{col+1}-{lev+1}'

                    # Jeżeli lokalizacja jest nowa
                    if not Location.objects.filter(name=location_name):
                        Location.objects.create(name=location_name, parent_shelf=shelf, level_index=lev+1, column_index=col+1)

            # Usuwanie nadmiarowych lokalizacji
            for elem in shelf.locations.filter(column_index__gt=columns):
                elem.delete()
            for elem in shelf.locations.filter(level_index__gt=levels):
                elem.delete()

            return redirect(shelf.get_absolute_url())
        else:
            messages.error(request, 'Nie udało się zaktualizować regału')

    context = {'shelf': shelf, 'locations': locations, 'locations_table': locations_table, 'edit_form': edit_form}
    return render(request, 'warehouse/locations/shelf_detail.html', context)


def shelf_delete(request, pk):
    shelf = get_object_or_404(Shelf, id=pk)

    finish_url = shelf.warehouse.get_absolute_url()
    if request.method == 'POST':
        shelf.delete()
    return redirect(finish_url)


def location_detail(request, pk):
    location = get_object_or_404(Location, id=pk)
    context = {'location': location}
    return render(request, 'warehouse/locations/location_detail.html', context)


def product_list(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'warehouse/products/product_list.html', context)


def product_create(request):

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pomyślnie dodano nowy produkt!')
            return redirect(reverse('warehouse:product_list'))
    else:
        form = ProductForm()

    context = {'form': form}
    return render(request, 'warehouse/products/product_create.html', context)


def product_detail(request, pk, slug):
    product = get_object_or_404(Product, id=pk)
    context = {'product': product}
    return render(request, 'warehouse/products/product_detail.html', context)


def product_delete(request, pk):
    product = get_object_or_404(Product, id=pk)
    if request.method == 'POST':
        product.delete()
        messages.warning(request, 'Produkt został usunięty')
    return redirect(reverse('warehouse:product_list'))
