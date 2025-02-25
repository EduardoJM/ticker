from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class StocksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.stocks"
    verbose_name = _('stocks')
