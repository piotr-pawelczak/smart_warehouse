import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator

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

@login_required
def goods_received_create(request, document_type):

    # document_type = 'pw'

    if document_type not in ['pz', 'pw']:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    ProductFormSet = inlineformset_factory(Document, ProductDocument, form=ProductDocumentReceivedForm, extra=1, can_delete=True)

    year = datetime.datetime.now().year
    lot_number = datetime.datetime.now().strftime("%d/%m/%Y")

    counter = 1
    if document_type == 'pz':
        if len(GoodsReceivedNote.objects.filter(created__year=year)) != 0:
            latest_document = GoodsReceivedNote.objects.filter(created__year=year).order_by('-created')[0]
            counter = int(latest_document.document_number.split('/')[2]) + 1
        document_number = f'PZ/{year}/{counter}'
    else:
        if len(InternalGoodsReceivedNote.objects.filter(created__year=year)) != 0:
            latest_document = InternalGoodsReceivedNote.objects.filter(created__year=year).order_by('-created')[0]
            counter = int(latest_document.document_number.split('/')[2]) + 1
        document_number = f'PW/{year}/{counter}'

    if request.method == 'POST':

        if document_type == 'pz':
            form = GoodsReceivedForm(request.POST)
        else:
            form = InternalGoodsReceivedForm(request.POST)

        formset = ProductFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():

            for cd in formset.cleaned_data:
                if len(cd) == 0:
                    messages.error(request, 'Poprawnie uzupełnij wszystkie pola. Jeżeli formularz dodawania produktu jest pusty, usuń go.')
                    return redirect(f'/document/{document_type}')

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

            new_document.user = request.user
            new_document.save()

            if new_document.confirmed:
                messages.success(request, f'Pomyślnie utworzono dokument {document_number}.')
            else:
                messages.success(request, f'Pomyślnie utworzono wersję roboczą dokumentu.')
            return redirect(reverse('documents:list'))
        else:
            messages.error(request, 'Poprawnie uzupełnij wszystkie pola. Jeżeli formularz dodawania produktu jest '
                                    'pusty, usuń go.')
    else:
        formset = ProductFormSet()

        if document_type == 'pz':
            form = GoodsReceivedForm()
        else:
            form = InternalGoodsReceivedForm()

    context = {'formset': formset, 'form': form, 'document_number': document_number, 'document_type': document_type}
    return render(request,
                  'documents/goods_received_note/goods_received_note_create.html', context)


@login_required
def goods_received_notes_update(request, document_type, pk):
    
    # document_type = 'pw'
    if document_type not in ['pz', 'pw']:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    document = Document.objects.get(id=pk)
    if document_type == 'pz':
        edit_form = GoodsReceivedForm(instance=document)
    else:
        edit_form = InternalGoodsReceivedForm(instance=document)

    ProductFormSet = inlineformset_factory(Document, ProductDocument, form=ProductDocumentReceivedForm, extra=0, can_delete=True)
    shelves = [x.location.parent_shelf for x in document.products.all()]
    formset = ProductFormSet(instance=document)

    for i in range(len(formset.forms)):
        formset.forms[i].fields['shelf'].initial = shelves[i]

    if request.method == 'POST':
        formset = ProductFormSet(request.POST, instance=document)

        if document_type == 'pz':
            edit_form = GoodsReceivedForm(request.POST, instance=document)
        else:
            edit_form = InternalGoodsReceivedForm(request.POST, instance=document)

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

            return redirect(reverse('documents:detail', args=[pk]))

    context = {'edit_form': edit_form, 'document_number': document.document_number, 'formset': formset, 'document_type': document_type}
    return render(request,
                  'documents/goods_received_note/goods_received_note_update.html', context)


class DocumentListView(LoginRequiredMixin, ListView):
    template_name = 'documents/list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        queryset = {
            'all_documents': Document.objects.all(),
            'confirmed_documents': Document.objects.filter(confirmed=True).order_by('-created'),
            'not_confirmed_documents': Document.objects.filter(confirmed=False).order_by('-created')
        }
        return queryset


class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    context_object_name = 'document'
    template_name = 'documents/detail.html'


def document_delete(request, pk):
    document = get_object_or_404(Document, id=pk)
    if request.method == 'POST' and not document.confirmed:
        document.delete()
        messages.warning(request, 'Dokument został usunięty')
    return redirect(reverse('documents:list'))


# ----------------------------------- Functions to handle AJAX form refresh --------------------------------------------

def load_product_locations(request):
    product_id = request.GET.get('product')
    locations = Product.objects.get(id=product_id).locations.filter(is_active=True)
    return render(request, 'documents/ajax_dropdown/productlocation_dropdown_list_options.html', {'locations': locations})


def load_shelves(request):
    warehouse_id = request.GET.get('warehouse')
    shelves = Warehouse.objects.get(id=warehouse_id).shelves.order_by('name', 'shelf_number').filter(is_active=True)
    return render(request, 'documents/ajax_dropdown/shelves_dropdown_list_options.html', {'shelves': shelves})


def load_locations(request):
    shelf_id = request.GET.get('shelf')
    locations = Shelf.objects.get(id=shelf_id).locations.filter(is_active=True)
    return render(request, 'documents/ajax_dropdown/locations_dropdown_list_options.html', {'locations': locations})


@login_required
def contractors_list(request):
    contractors = Contractor.objects.all()

    if request.method == 'POST':
        form = ContractorForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, 'Wystąpił problem podczas dodawania kontrahenta.')
    else:
        form = ContractorForm()

    context = {'contractors': contractors, 'form': form}
    return render(request, 'documents/contractors.html', context)


@login_required
def contractor_delete(request, pk):
    """
    Widok odpowiedzialny za usuwanie magazynu. Zostaje przekierowany do listy magazynów
    """
    contractor = get_object_or_404(Contractor, id=pk)
    if request.method == 'POST':
        contractor.delete()
        messages.warning(request, 'Kontrahent został usunięty')
    return redirect(reverse('documents:contractors'))


@login_required
def contractor_update(request, pk):
    contractor = get_object_or_404(Contractor, id=pk)

    if request.method == 'POST':
        edit_form = ContractorForm(request.POST, instance=contractor)
        if edit_form.is_valid():
            edit_form.save()
            return redirect(reverse('documents:contractors'))
    else:
        edit_form = ContractorForm(instance=contractor)

    context = {'edit_form': edit_form}
    return render(request, 'documents/update_contractor.html', context)

