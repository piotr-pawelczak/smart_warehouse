import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
# from django.urls import reverse

from documents.forms import *
from django.forms import inlineformset_factory
from warehouse.models import ProductLocation, Warehouse, Shelf
from django.views.generic import ListView
from custom_functions.documents import generate_number, generate_form


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
                    product_location = ProductLocation.objects.get(
                        product=new_product.product,
                        location=new_product.location,
                        lot_number=new_product.lot_number
                    )

                    if new_product.quantity > product_location.quantity:
                        messages.error(request, "Przekroczono dozwoloną ilość")
                        return redirect(reverse("documents:goods_issue_create"))
                    else:
                        product_location.quantity -= new_product.quantity
                        product_location.save()
                        if not product_location.quantity:
                            product_location.delete()

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
                        product_location = ProductLocation.objects.get(
                            product=updated_product.product,
                            location=updated_product.location,
                            lot_number=updated_product.lot_number
                        )

                        if updated_product.quantity > product_location.quantity:
                            messages.error(request, "Przekroczono dozwoloną ilość")
                            return redirect(reverse("documents:goods_issue_create"))
                        else:
                            product_location.quantity -= updated_product.quantity
                            product_location.save()
                            if not product_location.quantity:
                                product_location.delete()

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

                    new_product.lot_number = lot_number
                    new_product.save()

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
                        try:
                            product_location = ProductLocation.objects.get(
                                product=updated_product.product,
                                location=updated_product.location,
                                lot_number=lot_number
                            )
                            product_location.quantity += updated_product.quantity
                            product_location.save()

                        except(Exception,):
                            ProductLocation.objects.create(
                                product=updated_product.product,
                                location=updated_product.location,
                                lot_number=lot_number,
                                quantity=updated_product.quantity
                            )

            return redirect(reverse('documents:detail', args=[pk]))

    context = {'edit_form': edit_form, 'document_number': document.document_number,
               'formset': formset, 'document_type': document_type}
    return render(request,
                  'documents/goods_received_note/goods_received_note_update.html', context)


# -------------------------------------- General documents views ------------------------------------------------------

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
    context = {'document': document}
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
