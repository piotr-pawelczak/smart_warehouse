from django.shortcuts import render
import qrcode
import qrcode.image.svg
from io import BytesIO
import json
from warehouse.models import Warehouse, Shelf, Location
from .forms import WarehouseQrForm, ShelfQrForm, LocationQrForm

# Create your views here.


def home(request):
    warehouse_form = WarehouseQrForm()
    shelf_form = ShelfQrForm()
    location_form = LocationQrForm()

    if request.method == 'POST' and 'warehouse_submit' in request.POST:
        warehouse_form = WarehouseQrForm(request.POST)
        if warehouse_form.is_valid():
            warehouse = warehouse_form.cleaned_data["warehouse"]
            locations = Location.objects.filter(parent_shelf__warehouse_id=warehouse.id)
            locations_svg = get_locations_svg_zip(locations)
            context = {'locations_svg': locations_svg}
            return render(request, 'qr_labels/labels_to_print.html', context)

    elif request.method == 'POST' and 'shelf_submit' in request.POST:
        shelf_form = ShelfQrForm(request.POST)
        if shelf_form.is_valid():
            shelf = shelf_form.cleaned_data["shelf"]
            locations = Location.objects.filter(parent_shelf_id=shelf.id)
            locations_svg = get_locations_svg_zip(locations)
            context = {'locations_svg': locations_svg}
            return render(request, 'qr_labels/labels_to_print.html', context)
    elif request.method == 'POST' and 'location_submit' in request.POST:
        location_form = LocationQrForm(request.POST)
        if location_form.is_valid():
            locations = [location_form.cleaned_data["location"]]
            locations_svg = get_locations_svg_zip(locations)
            context = {'locations_svg': locations_svg}
            return render(request, 'qr_labels/labels_to_print.html', context)

    context = {'warehouse_form': warehouse_form, 'shelf_form': shelf_form, 'location_form': location_form}
    return render(request, "qr_labels/index.html", context)


def get_locations_svg_zip(locations):
    locations_data = [get_location_qr_data(elem) for elem in locations]
    locations_svg = [generate_svg(elem) for elem in locations_data]
    locations_svg = zip(locations, locations_svg)
    return locations_svg


def generate_svg(data):
    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(data, image_factory=factory, box_size=12)
    stream = BytesIO()
    img.save(stream)
    return stream.getvalue().decode()


def get_location_qr_data(location):
    data = {
        'id': location.id,
        'name': location.name
    }
    return json.dumps(data)



