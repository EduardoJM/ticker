import json
from functools import update_wrapper
from django.urls import reverse
from django.contrib import admin
from django.template.response import TemplateResponse
from django.contrib.admin.utils import unquote
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from domains.stocks.models import StockTimeSeries
from .models import Ticker, TickerPrice, TickerRename

@admin.register(TickerRename)
class TickerRenameAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'rename_to']
    list_display_links = ['id', 'code', 'rename_to']
    search_fields = ['code', 'rename_to']

@admin.register(Ticker)
class TickerAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'item_actions']
    list_display_links = ['id', 'code']
    search_fields = ['code']

    @admin.display(description=_('actions'))
    def item_actions(self, obj: Ticker):
        info = self.opts.app_label, self.opts.model_name
        return format_html(
            '<a href="%(evolution_url)s">%(evolution_text)s</a>' % {
                'evolution_url': reverse("admin:%s_%s_evolution" % info, kwargs={ 'object_id': obj.pk }),
                'evolution_text': _('evolution')
            },
        )

    def get_urls(self):
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.opts.app_label, self.opts.model_name
        
        return [
            path('<path:object_id>/evolution/', wrap(self.evolution_view), name="%s_%s_evolution" % info)
        ] + super().get_urls()
    
    def evolution_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        data = list(StockTimeSeries.objects.filter(ticker=obj).order_by('date').all())
        context = {
            **self.admin_site.each_context(request),
            'obj': obj,
            'data': data,
            'cumulated_value': json.dumps([float(x.cumulated_buy_value) for x in data]),
            'cumulated_adjusted_value': json.dumps([float(x.cumulated_adjusted_value) for x in data]),
            'cumulated_received': json.dumps([float(x.cumulated_received_value) for x in data]),
            'cumulated_and_received_value': json.dumps([float(x.cumulated_and_received_value) for x in data]),
            'quantity': json.dumps([x.cumulated_quantity for x in data]),
            **(extra_context or {}),
        }
        return TemplateResponse(
            request,
            "tickers/ticker_evolution.html",
            context,
        )

@admin.register(TickerPrice)
class TickerPriceAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticker', 'date_time', 'price']
    list_display_links = ['id', 'ticker', 'date_time', 'price']
