from django.db import models
from django.utils.translation import gettext_lazy as _

class TickerManager(models.Manager):
    def get_or_create_updated(self, code: str):
        ticker_rename = TickerRename.objects.filter(code=code).first()
        if not ticker_rename:
            return self.get_or_create(code=code)
        return self.get_or_create(code=ticker_rename.rename_to)

class Ticker(models.Model):
    code = models.CharField(_('code'), max_length=10, unique=True)

    objects = TickerManager()

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _('ticker')
        verbose_name_plural = _('tickers')
        ordering = ['code']

class TickerRename(models.Model):
    code = models.CharField(_('code'), max_length=10, unique=True)
    rename_to = models.CharField(_('code'), max_length=10)

    def __str__(self):
        return _('rename %(original_code)s to %(new_code)s') % {
            'original_code': self.code,
            'new_code': self.rename_to
        }

    class Meta:
        verbose_name = _('ticker rename')
        verbose_name_plural = _('tickers rename')

class TickerPrice(models.Model):
    ticker = models.ForeignKey(
        Ticker,
        verbose_name=_('ticker'),
        related_name='prices',
        on_delete=models.CASCADE
    )
    date_time = models.DateTimeField(_('date and time'), auto_now_add=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
