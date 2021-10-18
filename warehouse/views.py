from django.shortcuts import render, redirect
from .models import Warehouse, Location, Shelf
from django.shortcuts import get_object_or_404
from .forms import WarehouseForm, ShelfForm


def home_view(request):
    return render(request, 'warehouse/base.html')


def warehouse_list(request):
    warehouses = Warehouse.objects.all()

    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            form = WarehouseForm()

    else:
        form = WarehouseForm()

    return render(request, 'warehouse/warehouse_list.html', {'warehouses': warehouses, 'form': form})


def warehouse_detail(request, pk):
    warehouse = get_object_or_404(Warehouse, id=pk)
    shelves = warehouse.shelves.all()

    if request.method == 'POST':
        form = ShelfForm(request.POST)
        if form.is_valid():
            shelf = form.save(commit=False)
            shelf.warehouse = warehouse
            shelf.save()

            cols = form.cleaned_data['cols']
            rows = form.cleaned_data['rows']

            for r in range(rows):
                for c in range(cols):
                    location_name = f'{shelf.name}-{c+1}-{r+1}'
                    Location.objects.create(name=location_name, parent_shelf=shelf)

            form = ShelfForm()
    else:
        form = ShelfForm()

    return render(request, 'warehouse/warehouse_detail.html', {'warehouse': warehouse, 'form': form, 'shelves': shelves})


def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, id=pk)
    if request.method == 'POST':
        warehouse.delete()
    return redirect('/warehouses/')


def warehouse_edit(request, pk):
    warehouse = Warehouse.objects.get(id=pk)
    form = WarehouseForm(instance=warehouse)
    if request.method == 'POST':
        print(request.POST)
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            return redirect(f'/warehouse/{pk}')
    return render(request, 'warehouse/warehouse_edit.html', {'form': form})


def shelf_delete(request, pk):
    shelf = get_object_or_404(Shelf, id=pk)

    finish_url = shelf.warehouse.get_absolute_url()
    if request.method == 'POST':
        shelf.delete()
    return redirect(finish_url)


