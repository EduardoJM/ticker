from django.contrib import admin
from .models import Ticker

@admin.register(Ticker)
class TickerAdmin(admin.ModelAdmin):
    list_display = ['id', 'code']
    list_display_links = ['id', 'code']
    search_fields = ['code']
