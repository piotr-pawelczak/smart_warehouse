import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from documents.forms import *
from django.forms import inlineformset_factory
from warehouse.models import ProductLocation, Warehouse, Shelf
from django.views.generic import ListView, DetailView


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


# ------------------------------------------ Goods Received Note Views -------------------------------------------------

def goods_received_create(request):
    ProductFormSet = inlineformset_factory(Document, ProductDocument, form=ProductDocumentReceivedForm, extra=1, can_delete=True)

    year = datetime.datetime.now().year
    counter = len(GoodsReceivedNote.objects.filter(created__year='2021')) + 1
    if counter < 10:
        counter = f'0{counter}'
    document_number = f'PZ/{year}/{counter}'

    lot_number = datetime.datetime.now().strftime("%d/%m/%Y")

    if request.method == 'POST':
        form = GoodsReceivedForm(request.POST)
        formset = ProductFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():

            for cd in formset.cleaned_data:
                if len(cd) == 0:
                    messages.error(request, 'Poprawnie uzupełnij wszystkie pola. Jeżeli formularz dodawania produktu jest pusty, usuń go.')
                    return redirect('/document/pz')

            new_document = form.save(commit=False)
            new_document.document_number = document_number
            new_document.save()

            for product_form in formset.forms:
                new_product = product_form.save(commit=False)
                new_product.document = new_document
                new_product.save()

                if new_document.confirmed:
                    try:
                        product_location = ProductLocation.objects.get(
                            product=new_product.product,
                            location=new_product.location,
                            lot_number=lot_number
                        )
                        product_location.quantity += new_product.quantity
                        product_location.save()

                    except(Exception,):
                        ProductLocation.objects.create(
                            product=new_product.product,
                            location=new_product.location,
                            lot_number=lot_number,
                            quantity=new_product.quantity
                        )

            if new_document.confirmed:
                messages.success(request, f'Pomyślnie utworzono dokument {document_number}.')
            else:
                messages.success(request, f'Pomyślnie utworzono wersję roboczą dokumentu.')
            return redirect(reverse('documents:list'))
        else:
            messages.error(request, 'Poprawnie uzupełnij wszystkie pola. Jeżeli formularz dodawania produktu jest '
                                    'pusty, usuń go.')
    else:
        form = GoodsReceivedForm()
        formset = ProductFormSet()

    context = {'formset': formset, 'form': form, 'document_number': document_number}
    return render(request, 'documents/goods_received_note_create.html', context)


def goods_received_notes_update(request):
    ProductFormSet = inlineformset_factory(Document, ProductDocument, form=ProductDocumentReceivedForm, extra=0, can_delete=True)
    grn = GoodsReceivedNote.objects.get(id=121)

    shelves = [x.location.parent_shelf for x in grn.products.all()]

    edit_form = GoodsReceivedForm(instance=grn)
    formset = ProductFormSet(instance=grn)

    for i in range(len(formset.forms)):
        formset.forms[i].fields['shelf'].initial = shelves[i]

    if request.method == 'POST':
        formset = ProductFormSet(request.POST, instance=grn)
        edit_form = GoodsReceivedForm(request.POST, instance=grn)
        if edit_form.is_valid() and formset.is_valid():
            updated_document = edit_form.save()

            for form in formset.forms:
                if form.cleaned_data['DELETE']:
                    product_document_id = form.cleaned_data['id'].id
                    obj = ProductDocument.objects.get(id=product_document_id)
                    obj.delete()
                else:
                    updated_product = form.save(commit=False)
                    updated_product.document = updated_document
                    updated_product.save()

            return redirect('warehouse:home')

    context = {'edit_form': edit_form, 'document_number': grn.document_number, 'formset': formset}
    return render(request, 'documents/goods_received_note_update.html', context)


class DocumentListView(ListView):
    template_name = 'documents/list.html'
    queryset = Document.objects.all().order_by('-created')
    context_object_name = 'documents'


class DocumentDetailView(DetailView):
    model = Document
    context_object_name = 'document'
    template_name = 'documents/detail.html'

# ----------------------------------- Functions to handle AJAX form refresh --------------------------------------------


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