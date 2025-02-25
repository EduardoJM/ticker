from django.db import models
from django.utils.translation import gettext_lazy as _

class Ticker(models.Model):
    code = models.CharField(_('code'), max_length=10, unique=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _('ticker')
        verbose_name_plural = _('tickers')
        ordering = ['code']
