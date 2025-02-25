from django.db import models
from django.utils.translation import gettext_lazy as _

class Tax(models.Model):
    name = models.CharField(_('name'), max_length=200)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('tax')
        verbose_name_plural = _('taxes')

class TradingNote(models.Model):
    number = models.CharField(_('number'), max_length=100)
    trading_date = models.DateField(_('trading date'))
    liquidation_date = models.DateField(_('liquidation date'))
    total_value = models.DecimalField(_('total value'), max_digits=15, decimal_places=2)
    total_taxes = models.DecimalField(_('total taxes'), max_digits=15, decimal_places=2)
    net_value = models.DecimalField(_('net value'), max_digits=15, decimal_places=2)

    def __str__(self):
        return self.number
    
    class Meta:
        verbose_name = _('trading note')
        verbose_name_plural = _('trading notes')
        ordering = ['-trading_date']

class TradingTax(models.Model):
    trading_note = models.ForeignKey(
        TradingNote,
        on_delete=models.CASCADE,
        verbose_name=_('trading note'),
        related_name='taxes',
    )
    tax = models.ForeignKey(
        Tax,
        on_delete=models.CASCADE,
        verbose_name=_('tax'),
    )
    value = models.DecimalField(_('value'), max_digits=15, decimal_places=2)

    def __str__(self):
        return _('%(tax)s: %(value)s') % {
            'tax': str(self.tax),
            'value': str(self.value),
        }

    class Meta:
        verbose_name = _('trading tax')
        verbose_name_plural = _('trading taxes')

class TradingStock(models.Model):
    TYPE_BUY = 'BUY'
    TYPE_SALE = 'SALE'
    TYPES = (
        (TYPE_BUY, _('buy')),
        (TYPE_SALE, _('sale')),
    )

    trading_note = models.ForeignKey(
        TradingNote,
        on_delete=models.CASCADE,
        verbose_name=_('trading note'),
        related_name='stocks',
    )
    ticker = models.ForeignKey(
        'tickers.Ticker',
        on_delete=models.CASCADE,
        verbose_name=_('ticker')
    )
    quantity = models.IntegerField(_('quantity'))
    unit_price = models.DecimalField(_('unit price'), max_digits=12, decimal_places=2)
    trading_type = models.CharField(_('trading type'), choices=TYPES, default=TYPE_BUY)

    def __str__(self):
        return _('%(quantity)s units of %(ticker)s') % {
            'quantity': str(self.quantity),
            'ticker': str(self.ticker),
        }

    class Meta:
        verbose_name = _('trading stock')
        verbose_name_plural = _('trading stocks')

class StockTimeSeries(models.Model):
    ticker = models.ForeignKey(
        'tickers.Ticker',
        on_delete=models.CASCADE,
        verbose_name=_('ticker')
    )
    date = models.DateField(_('date'))
    quantity = models.IntegerField(_('quantity'))
    cumulated_quantity = models.IntegerField(_('cumulated quantity'))
    buy_value = models.DecimalField(_('buy value'), max_digits=12, decimal_places=2)
    cumulated_buy_value = models.DecimalField(_('cumulated buy value'), max_digits=12, decimal_places=2)
    received_value = models.DecimalField(_('received value'), max_digits=12, decimal_places=2)
    cumulated_received_value = models.DecimalField(_('cumulated received value'), max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['-date']
        verbose_name = _('stock time series')
        verbose_name_plural = _('stock time series')
