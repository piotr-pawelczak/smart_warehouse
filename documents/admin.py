from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin
from .models import *

# Register your models here.


class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    raw_id_fields = ['product']


@admin.register(GoodsIssueNote)
class GoodsIssueNoteAdmin(PolymorphicChildModelAdmin):
    base_model = GoodsIssueNote
    inlines = [ProductDocumentInline]


@admin.register(InternalGoodsIssueNote)
class InternalGoodsIssueNoteAdmin(PolymorphicChildModelAdmin):
    base_model = InternalGoodsIssueNote
    inlines = [ProductDocumentInline]


@admin.register(GoodsReceivedNote)
class GoodsReceivedNoteAdmin(PolymorphicChildModelAdmin):
    base_model = GoodsReceivedNote
    inlines = [ProductDocumentInline]
    list_display = ['document_number', 'confirmed', 'created']


@admin.register(InternalGoodsReceivedNote)
class InternalGoodsReceivedNoteAdmin(PolymorphicChildModelAdmin):
    base_model = InternalGoodsReceivedNote
    inlines = [ProductDocumentInline]
    list_display = ['document_number', 'confirmed', 'created']


@admin.register(Document)
class DocumentAdmin(PolymorphicParentModelAdmin):
    base_model = Document
    child_models = (GoodsIssueNote, InternalGoodsIssueNote, GoodsReceivedNote, InternalGoodsReceivedNote)
    list_display = ['document_number', 'confirmed', 'created']


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
