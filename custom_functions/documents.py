import datetime

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from documents.models import GoodsReceivedNote, InternalGoodsReceivedNote, GoodsIssueNote, InternalGoodsIssueNote, \
    InterBranchTransferMinus, InterBranchTransferPlus
from documents.forms import GoodsReceivedForm, InternalGoodsReceivedForm, GoodsIssueForm, InternalGoodsIssueForm, \
    InterBranchTransferMinusForm
from warehouse.models import ProductLocation


def generate_number(document_type):
    counter = 1
    year = datetime.datetime.now().year
    document_number = None

    if document_type == 'pz':
        if len(GoodsReceivedNote.objects.filter(created__year=year)) != 0:
            latest_document = GoodsReceivedNote.objects.filter(created__year=year).order_by('-created')[0]
            counter = int(latest_document.document_number.split('/')[2]) + 1
        document_number = f'PZ/{year}/{counter}'
    elif document_type == 'pw':
        if len(InternalGoodsReceivedNote.objects.filter(created__year=year)) != 0:
            latest_document = InternalGoodsReceivedNote.objects.filter(created__year=year).order_by('-created')[0]
            counter = int(latest_document.document_number.split('/')[2]) + 1
        document_number = f'PW/{year}/{counter}'
    elif document_type == 'wz':
        if len(GoodsIssueNote.objects.filter(created__year=year)) != 0:
            latest_document = GoodsIssueNote.objects.filter(created__year=year).order_by('-created')[0]
            counter = int(latest_document.document_number.split('/')[2]) + 1
        document_number = f'WZ/{year}/{counter}'
    elif document_type == 'rw':
        if len(InternalGoodsIssueNote.objects.filter(created__year=year)) != 0:
            latest_document = InternalGoodsIssueNote.objects.filter(created__year=year).order_by('-created')[0]
            counter = int(latest_document.document_number.split('/')[2]) + 1
        document_number = f'RW/{year}/{counter}'
    elif document_type == 'mm-':
        if len(InterBranchTransferMinus.objects.filter(created__year=year)) != 0:
            latest_document = InterBranchTransferMinus.objects.filter(created__year=year).order_by('-created')[0]
            counter = int(latest_document.document_number.split('/')[2]) + 1
        document_number = f'MM-/{year}/{counter}'
    elif document_type == 'mm+':
        if len(InterBranchTransferPlus.objects.filter(created__year=year)) != 0:
            latest_document = InterBranchTransferPlus.objects.filter(created__year=year).order_by('-created')[0]
            counter = int(latest_document.document_number.split('/')[2]) + 1
        document_number = f'MM+/{year}/{counter}'

    return document_number


def generate_form(document_type, data=None):
    form = None
    if document_type == 'pz':
        form = GoodsReceivedForm(data)
    elif document_type == 'pw':
        form = InternalGoodsReceivedForm(data)
    elif document_type == 'wz':
        form = GoodsIssueForm(data)
    elif document_type == 'rw':
        form = InternalGoodsIssueForm(data)
    elif document_type == 'mm-':
        form = InterBranchTransferMinusForm(data)

    return form


def add_quantity(product_document, lot_number=None):
    if lot_number:
        product_document.lot_number = lot_number
        product_document.save()

    try:
        product_location = ProductLocation.objects.get(
            product=product_document.product,
            location=product_document.location,
            lot_number=product_document.lot_number
        )
        product_location.quantity += product_document.quantity
        product_location.save()

    except(Exception,):
        ProductLocation.objects.create(
            product=product_document.product,
            location=product_document.location,
            lot_number=product_document.lot_number,
            quantity=product_document.quantity
        )


def add_quantity_transfer(product_transfer):
    try:
        product_location = ProductLocation.objects.get(
            product=product_transfer.product,
            location=product_transfer.location_target,
            lot_number=product_transfer.lot_number
        )
        product_location.quantity += product_transfer.quantity
        product_location.save()

    except(Exception,):
        ProductLocation.objects.create(
            product=product_transfer.product,
            location=product_transfer.location_target,
            lot_number=product_transfer.lot_number,
            quantity=product_transfer.quantity
        )


def remove_quantity(request, product_document):
    product_location = ProductLocation.objects.get(
        product=product_document.product,
        location=product_document.location,
        lot_number=product_document.lot_number
    )

    if product_document.quantity > product_location.quantity:
        messages.error(request, "Przekroczono dozwoloną ilość")
        return redirect(reverse("documents:goods_issue_create"))
    else:
        product_location.quantity -= product_document.quantity
        product_location.save()
        if not product_location.quantity:
            product_location.delete()


def remove_quantity_transfer(request, product_transfer):
    product_location = ProductLocation.objects.get(
        product=product_transfer.product,
        location=product_transfer.location,
        lot_number=product_transfer.lot_number
    )

    if product_transfer.quantity > product_location.quantity:
        messages.error(request, "Przekroczono dozwoloną ilość")
        return redirect(reverse("documents:goods_issue_create"))
    else:
        product_location.quantity -= product_transfer.quantity
        product_location.save()
        if not product_location.quantity:
            product_location.delete()
