from django.contrib import admin
from domains.admin.filters.autocomplete_related import (
    AutocompleteRelatedFilter,
    AutocompleteRelatedFilterMixin,
)
from .models import TradingNote, TradingStock, TradingTax, Tax, StockTimeSeries

@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']
    search_fields = ['name']

class TradingTaxInlineAdmin(admin.StackedInline):
    model = TradingTax
    autocomplete_fields = ['tax']
    extra = 0

class TradingStockInlineAdmin(admin.StackedInline):
    model = TradingStock
    autocomplete_fields = ['ticker']
    extra = 0

@admin.register(TradingStock)
class TradingStockAdmin(admin.ModelAdmin):
    list_display = ['id', 'trading_note', 'ticker', 'trading_type', 'quantity', 'unit_price']
    list_display_links = ['id', 'trading_note', 'ticker', 'trading_type', 'quantity', 'unit_price']
    search_fields = ['ticker__code']

@admin.register(TradingNote)
class TradingNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'liquidation_date', 'net_value']
    inlines = [
        TradingTaxInlineAdmin,
        TradingStockInlineAdmin,
    ]

@admin.register(StockTimeSeries)
class StockTimeSeriesAdmin(AutocompleteRelatedFilterMixin, admin.ModelAdmin):
    list_display = ['ticker', 'date', 'quantity', 'cumulated_quantity', 'buy_value', 'cumulated_buy_value', 'received_value', 'cumulated_received_value', 'average_cost']
    list_filter = [
        ('ticker', AutocompleteRelatedFilter),
    ]
