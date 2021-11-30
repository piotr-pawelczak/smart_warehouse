import datetime

from documents.models import GoodsReceivedNote, InternalGoodsReceivedNote, GoodsIssueNote, InternalGoodsIssueNote
from documents.forms import GoodsReceivedForm, InternalGoodsReceivedForm, GoodsIssueForm, InternalGoodsIssueForm

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

    return form



