from django.contrib import admin
from .models import *
from django.urls import reverse
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
# Register your models here

@admin.register(Semester)
@admin.register(Subject)
@admin.register(Topic)

@admin.register(Question)
@admin.register(Choice)

class ViewAdmin(ImportExportModelAdmin):
    pass