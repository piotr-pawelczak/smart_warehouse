from django.shortcuts import render, redirect
from .models import Warehouse, Location, Shelf
from django.shortcuts import get_object_or_404
from .forms import WarehouseForm, ShelfForm
from django.contrib import messages
import numpy as np


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
            form = WarehouseForm()
    else:
        form = WarehouseForm()

    return render(request, 'warehouse/warehouse_list.html', {'warehouses': warehouses, 'form': form})


def warehouse_detail(request, pk):
    """
    Widok do obsługi pojedynczego magazynu
    Magazyn jest pobierany poprzez identyfikator
    Zawiera informacje dotyczące magazynu, pozwala na modyfikacje magazynu
    Z poziomu tego widoku można dodawać regały
    """

    warehouse = get_object_or_404(Warehouse, id=pk)
    shelves = warehouse.shelves.all().order_by('name')

    if shelves.count() == 0:
        default_number = 1
    else:
        default_number = shelves.reverse()[0].shelf_number + 1

    # Formularz do edycji magazynu
    edit_form = WarehouseForm(instance=warehouse)
    if request.method == 'POST' and 'description' in request.POST:
        edit_form = WarehouseForm(request.POST, instance=warehouse)
        if edit_form.is_valid():
            edit_form.save()

    # Formularz do utworzenia regału
    if request.method == 'POST' and 'description' not in request.POST:
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
            default_number = shelves.reverse()[0].shelf_number + 1
            form = ShelfForm(initial={'shelf_number': default_number})

            # Utworzenie lokalizacji
            for lev in range(rows):
                for col in range(cols):
                    location_name = f'{shelf.name}-{col+1}-{lev+1}'
                    Location.objects.create(name=location_name, parent_shelf=shelf, level_index=lev, column_index=col)

    else:
        form = ShelfForm(initial={'shelf_number': default_number})

    return render(request, 'warehouse/warehouse_detail.html', {'warehouse': warehouse, 'form': form, 'shelves': shelves, 'edit_form': edit_form})


def warehouse_delete(request, pk):
    """
    Widok odpowiedzialny za usuwanie magazynu. Zostaje przekierowany do listy magazynów
    """
    warehouse = get_object_or_404(Warehouse, id=pk)
    if request.method == 'POST':
        warehouse.delete()
    return redirect('/warehouses/')


def shelf_detail(request, pk):
    shelf = get_object_or_404(Shelf, id=pk)
    locations = shelf.locations.all()

    # Zamiana listy obiektów na tablicę
    n = shelf.levels
    table = list(locations)
    table_2d = [table[i:i+n] for i in range(0, len(table), n)]
    locations_table = list(map(list, zip(*table_2d)))
    locations_table.reverse()

    context = {'shelf': shelf, 'locations': locations, 'locations_table': locations_table}
    return render(request, 'warehouse/shelf_detail.html', context)


def shelf_delete(request, pk):
    shelf = get_object_or_404(Shelf, id=pk)

    finish_url = shelf.warehouse.get_absolute_url()
    if request.method == 'POST':
        shelf.delete()
    return redirect(finish_url)


