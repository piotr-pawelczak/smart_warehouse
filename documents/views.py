import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
import copy

from documents.forms import *
from django.forms import inlineformset_factory
from warehouse.models import ProductLocation, Warehouse, Shelf
from django.views.generic import ListView
from custom_functions.documents import generate_number, generate_form, add_quantity, remove_quantity, \
    add_quantity_transfer, remove_quantity_transfer


# ----------------------------------------- Goods Issue Note Views -----------------------------------------------------

@login_required
def goods_issue_create(request, document_type):

    if document_type not in ['wz', 'rw']:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    document_number = generate_number(document_type)
    ProductFormSet = inlineformset_factory(Document, ProductDocument, form=ProductDocumentIssueForm, extra=1,
                                           can_delete=True)

    if request.method == 'POST':
        form = generate_form(document_type, request.POST)
        formset = ProductFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            new_document = form.save(commit=False)
            new_document.document_number = document_number
            new_document.user = request.user
            new_document.save()

            for product_form in formset:
                new_product = product_form.save(commit=False)
                new_product.document = new_document
                new_product.save()

                if new_document.confirmed:
                    remove_quantity(request, new_product)

            if new_document.confirmed:
                messages.success(request, f'Pomyślnie utworzono dokument {document_number}.')
            else:
                messages.success(request, f'Pomyślnie utworzono wersję roboczą dokumentu.')
            return redirect(reverse('documents:list'))
    else:
        form = generate_form(document_type)
        formset = ProductFormSet()

    context = {'form': form, 'document_number': document_number, 'formset': formset, 'document_type': document_type}
    return render(request, 'documents/goods_issue_note/goods_issue_note_create.html', context)


def goods_issue_update(request, document_type, pk):

    if document_type not in ['wz', 'rw']:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    document = Document.objects.get(id=pk)

    if document_type == 'wz':
        edit_form = GoodsIssueForm(instance=document)
    else:
        edit_form = InternalGoodsIssueForm(instance=document)

    ProductFormSet = inlineformset_factory(Document, ProductDocument, form=ProductDocumentIssueForm, extra=0,
                                           can_delete=True)
    formset = ProductFormSet(instance=document)

    if request.method == 'POST':
        formset = ProductFormSet(request.POST, instance=document)

        if document_type == 'wz':
            edit_form = GoodsIssueForm(request.POST, instance=document)
        else:
            edit_form = InternalGoodsIssueForm(request.POST, instance=document)

        if formset.is_valid() and edit_form.is_valid():
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

                    if updated_document.confirmed:
                        remove_quantity(request, updated_product)

            return redirect(reverse('documents:detail', args=[pk]))

    context = {'document': document, 'edit_form': edit_form, 'formset': formset, 'document_type': document_type}
    return render(request, 'documents/goods_issue_note/goods_issue_note_update.html', context)


# ------------------------------------------ Goods Received Note Views -------------------------------------------------

@login_required
def goods_received_create(request, document_type):

    if document_type not in ['pz', 'pw']:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    ProductFormSet = inlineformset_factory(Document, ProductDocument, form=ProductDocumentReceivedForm, extra=1,
                                           can_delete=True)

    lot_number = datetime.datetime.now().strftime("%d/%m/%Y")
    document_number = generate_number(document_type)

    if request.method == 'POST':
        form = generate_form(document_type, request.POST)
        formset = ProductFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            new_document = form.save(commit=False)
            new_document.document_number = document_number
            new_document.user = request.user
            new_document.save()

            for product_form in formset.forms:
                new_product = product_form.save(commit=False)
                new_product.document = new_document
                new_product.save()

                if new_document.confirmed:
                    add_quantity(new_product, lot_number)

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
        form = generate_form(document_type)

    context = {'formset': formset, 'form': form, 'document_number': document_number, 'document_type': document_type}
    return render(request,
                  'documents/goods_received_note/goods_received_note_create.html', context)


@login_required
def goods_received_notes_update(request, document_type, pk):

    if document_type not in ['pz', 'pw']:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    document = Document.objects.get(id=pk)
    if document_type == 'pz':
        edit_form = GoodsReceivedForm(instance=document)
    else:
        edit_form = InternalGoodsReceivedForm(instance=document)

    ProductFormSet = inlineformset_factory(Document, ProductDocument, form=ProductDocumentReceivedForm, extra=0,
                                           can_delete=True)
    shelves = [x.location.parent_shelf for x in document.products.all()]
    formset = ProductFormSet(instance=document)
    lot_number = datetime.datetime.now().strftime("%d/%m/%Y")

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

                    if updated_document.confirmed:
                        add_quantity(updated_product, lot_number)

            return redirect(reverse('documents:detail', args=[pk]))

    context = {'edit_form': edit_form, 'document_number': document.document_number,
               'formset': formset, 'document_type': document_type}
    return render(request,
                  'documents/goods_received_note/goods_received_note_update.html', context)


# ------------------------------------------ Interbranch Transfer Views ------------------------------------------------

def interbranch_transfer_create(request):

    document_type = 'mm-'
    document_number = generate_number(document_type)

    ProductFormSet = inlineformset_factory(Document, ProductTransfer, form=ProductTransferForm, extra=1,
                                           can_delete=True)

    if request.method == 'POST':
        form = InterBranchTransferMinusForm(request.POST)
        formset = ProductFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            new_document = form.save(commit=False)
            new_document.document_number = document_number
            new_document.user = request.user
            new_document.save()

            for product_form in formset:
                new_product = product_form.save(commit=False)
                new_product.document = new_document
                new_product.save()

                if new_document.confirmed:
                    add_quantity_transfer(new_product)
                    remove_quantity_transfer(request, new_product)

            if new_document.confirmed:
                new_transfer_plus = InterBranchTransferPlus.objects.create(
                    document_number=generate_number('mm+'),
                    confirmed=True,
                    warehouse=new_document.target_warehouse,
                    source_warehouse=new_document.warehouse,
                    user=new_document.user
                )

                transfer_minus_products = [elem.id for elem in new_document.products.all()]
                transfer_plus_products = ProductTransfer.objects.filter(id__in=transfer_minus_products)

                for product_transfer in transfer_plus_products:
                    ProductTransfer.objects.create(
                        product=product_transfer.product,
                        location=product_transfer.location,
                        quantity=product_transfer.quantity,
                        price=product_transfer.price,
                        lot_number=product_transfer.lot_number,
                        location_target=product_transfer.location_target,
                        document=new_transfer_plus
                    )

            return redirect(reverse('documents:list'))
    else:
        form = InterBranchTransferMinusForm()
        formset = ProductFormSet()

    context = {'document_number': document_number, 'form': form, 'formset': formset}
    return render(request, 'documents/interbranch_transfer/interbranch_transfer_create.html', context)


def interbranch_transfer_update(request, pk):
    document = InterBranchTransferMinus.objects.get(id=pk)
    edit_form = InterBranchTransferMinusForm(instance=document)
    ProductFormSet = inlineformset_factory(Document, ProductTransfer, form=ProductTransferForm, can_delete=True, extra=0)
    formset = ProductFormSet(instance=document)

    if request.method == 'POST':
        formset = ProductFormSet(request.POST, instance=document)
        edit_form = InterBranchTransferMinusForm(request.POST, instance=document)

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

                    if updated_document.confirmed:
                        add_quantity_transfer(updated_product)
                        remove_quantity_transfer(request, updated_product)

            if updated_document.confirmed:
                new_transfer_plus = InterBranchTransferPlus.objects.create(
                    document_number=generate_number('mm+'),
                    confirmed=True,
                    warehouse=updated_document.target_warehouse,
                    source_warehouse=updated_document.warehouse,
                    user=updated_document.user
                )

                transfer_minus_products = [elem.id for elem in updated_document.products.all()]
                transfer_plus_products = ProductTransfer.objects.filter(id__in=transfer_minus_products)

                for product_transfer in transfer_plus_products:
                    ProductTransfer.objects.create(
                        product=product_transfer.product,
                        location=product_transfer.location,
                        quantity=product_transfer.quantity,
                        price=product_transfer.price,
                        lot_number=product_transfer.lot_number,
                        location_target=product_transfer.location_target,
                        document=new_transfer_plus
                    )
        else:
            print(formset.errors)

        return redirect("documents:list")

    context = {'document': document, 'edit_form': edit_form, 'formset': formset}
    return render(request, 'documents/interbranch_transfer/interbranch_transfer_update.html', context)


# -------------------------------------- General documents views -------------------------------------------------------

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


def document_detail(request, pk):
    document = Document.objects.get(id=pk)
    transfer_products = ProductTransfer.objects.none()

    if document.document_type in ['MM+', 'MM-']:
        products_ids = [elem.id for elem in document.products.all()]
        transfer_products = ProductTransfer.objects.filter(id__in=products_ids)

    context = {'document': document, 'transfer_products': transfer_products}
    return render(request, 'documents/detail.html', context)


def document_delete(request, pk):
    document = get_object_or_404(Document, id=pk)
    if request.method == 'POST' and not document.confirmed:
        document.delete()
        messages.warning(request, 'Dokument został usunięty')
    return redirect(reverse('documents:list'))


# ----------------------------------- Functions to handle AJAX form refresh --------------------------------------------

def load_warehouse_products(request):
    warehouse_id = request.GET.get('warehouse')
    products = Warehouse.objects.get(id=warehouse_id).get_available_products()
    return render(request, 'documents/ajax_dropdown/warehouse_products_list_dropdown.html', {'products': products})


def load_product_locations(request):
    product_id = request.GET.get('product')
    warehouse_id = request.GET.get('warehouse_product')
    locations = Product.objects.get(id=product_id).locations.filter(location__parent_shelf__warehouse_id=warehouse_id,
                                                                    location__is_active=True,
                                                                    location__parent_shelf__is_active=True
                                                                    )
    context = {'locations': locations}
    return render(request, 'documents/ajax_dropdown/productlocation_dropdown_list_options.html', context)


def load_shelves(request):
    warehouse_id = request.GET.get('warehouse')
    shelves = Warehouse.objects.get(id=warehouse_id).shelves.order_by('name', 'shelf_number').filter(is_active=True)
    return render(request, 'documents/ajax_dropdown/shelves_dropdown_list_options.html', {'shelves': shelves})


def load_locations(request):
    shelf_id = request.GET.get('shelf')
    locations = Shelf.objects.get(id=shelf_id).locations.filter(is_active=True)
    return render(request, 'documents/ajax_dropdown/locations_dropdown_list_options.html', {'locations': locations})


def load_target_locations(request):
    warehouse_id = request.GET.get('target-warehouse')
    locations = Location.objects.filter(parent_shelf__warehouse_id=warehouse_id)
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
