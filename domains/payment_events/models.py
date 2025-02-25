from django.db import models
from django.utils.translation import gettext_lazy as _

class PaymentEvent(models.Model):
    TYPE_INCOME = 'income'
    TYPE_DIVIDEND = 'dividend'
    TYPE_INTEREST_ON_EQUITY = 'interest_on_equity'
    TYPES = (
        (TYPE_INCOME, _('income')),
        (TYPE_DIVIDEND, _('dividend')),
        (TYPE_INTEREST_ON_EQUITY, _('interest on equity')),
    )
    
    ticker = models.ForeignKey(
        'tickers.Ticker',
        on_delete=models.CASCADE,
        verbose_name=_('ticker')
    )
    event_type = models.CharField(
        _('event type'),
        choices=TYPES,
        max_length=20,
    )
    quantity = models.IntegerField(_('quantity'))
    unit_price = models.DecimalField(_('unit price'), max_digits=15, decimal_places=2)
    net_value = models.DecimalField(_('net value'), max_digits=15, decimal_places=2)
    date = models.DateField(_('date'))

    def __str__(self):
        return _('%(ticker)s payed %(value)s on %(date)s') % {
            'ticker': str(self.ticker),
            'value': str(self.net_value),
            'date': str(self.date)
        }

    class Meta:
        verbose_name = _('payment event')
        verbose_name_plural = _('payment events')
        constraints = [
            models.UniqueConstraint(
                fields=['ticker', 'event_type', 'date'],
                name='unique_payment_event'
            )
        ]
        ordering = ['-date']
