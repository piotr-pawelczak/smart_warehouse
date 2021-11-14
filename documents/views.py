from django.shortcuts import render, redirect
from documents.forms import *
from django.forms import formset_factory


# Create your views here.
def goods_issue_create(request):
    document_type = 'GIN'
    if request.method == 'POST':
        form = GoodsIssueForm(request.POST)
        form_product = ProductDocumentForm(document_type, request.POST)
        if form.is_valid():
            form.save()
            form_product.save()
    else:
        form = GoodsIssueForm()
        form_product = ProductDocumentForm(document_type)

    context = {'form': form, 'form_product': form_product, 'document_type': document_type}
    return render(request, 'documents/create_document.html', context)


def goods_received_create(request):
    ProductFormSet = formset_factory(ProductDocumentReceivedForm, extra=1)

    year = datetime.datetime.now().year
    counter = len(GoodsReceivedNote.objects.filter(created__year='2021')) + 1
    document_number = f'PZ/{year}/{counter}'

    if request.method == 'POST':
        form = GoodsReceivedForm(request.POST)
        formset = ProductFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            new_document = form.save(commit=False)
            new_document.document_number = document_number
            new_document.save()
            for product_form in formset.forms:
                new_product = product_form.save(commit=False)
                new_product.document = new_document
                new_product.save()
            return redirect(reverse('documents:document_create'))

    else:
        form = GoodsReceivedForm()
        formset = ProductFormSet()

    context = {'formset': formset, 'form': form, 'document_number': document_number}
    return render(request, 'documents/goods_received_note_create.html', context)


def load_product_locations(request):
    product_id = request.GET.get('product')
    locations = Product.objects.get(id=product_id).locations.all()
    return render(request, 'documents/ajax_dropdown/productlocation_dropdown_list_options.html', {'locations': locations})


def load_shelves(request):
    warehouse_id = request.GET.get('warehouse')
    shelves = Warehouse.objects.get(id=warehouse_id).shelves.all()
    return render(request, 'documents/ajax_dropdown/shelves_dropdown_list_options.html', {'shelves': shelves})


def load_locations(request):
    shelf_id = request.GET.get('shelf')
    locations = Shelf.objects.get(id=shelf_id).locations.all()
    return render(request, 'documents/ajax_dropdown/locations_dropdown_list_options.html', {'locations': locations})