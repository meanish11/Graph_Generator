# data_analyzer/admin.py
from django.contrib import admin
from .models import ExcelFile

@admin.register(ExcelFile)
class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'uploaded_at', 'file']
    list_filter = ['uploaded_at']
    search_fields = ['name']
    date_hierarchy = 'uploaded_at'