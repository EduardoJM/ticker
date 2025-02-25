from django.utils import timezone
from decimal import Decimal
from domains.tickers.models import Ticker
from domains.payment_events.models import PaymentEvent
from domains.stocks.models import TradingStock, StockTimeSeries

def sort_events(instance: TradingStock | PaymentEvent):
    if isinstance(instance, TradingStock):
        return instance.trading_note.trading_date
    return instance.date

def create_time_series(
    instance: TradingStock | PaymentEvent,
    cumulated_quantity: int,
    cumulated_buy_value: Decimal,
    cumulated_received_value: Decimal,
):
    if isinstance(instance, TradingStock):
        date = instance.trading_note.trading_date
        quantity = instance.quantity
        buy_value = instance.unit_price * quantity
        new_quantity = cumulated_quantity + quantity
        new_buy_value = buy_value + cumulated_buy_value
        obj, _ = StockTimeSeries.objects.update_or_create(
            ticker=instance.ticker,
            date=date,
            defaults={
                'quantity': quantity,
                'cumulated_quantity': new_quantity,
                'buy_value': buy_value,
                'cumulated_buy_value': new_buy_value,
                'received_value': 0,
                'cumulated_received_value': cumulated_received_value,
            }
        )
        return obj, new_quantity, new_buy_value, cumulated_received_value

    date = instance.date
    new_received_value = cumulated_received_value + instance.net_value
    obj, _ = StockTimeSeries.objects.update_or_create(
        ticker=instance.ticker,
        date=date,
        defaults={
            'quantity': 0,
            'cumulated_quantity': cumulated_quantity,
            'buy_value': 0,
            'cumulated_buy_value': cumulated_buy_value,
            'received_value': instance.net_value,
            'cumulated_received_value': new_received_value,
        }
    )
    return obj, cumulated_quantity, cumulated_buy_value, new_received_value

def compute(ticker: Ticker):
    stocks = list(
        TradingStock.objects
        .select_related('trading_note')
        .filter(ticker=ticker)
        .all()
    )
    events = list(PaymentEvent.objects.filter(ticker=ticker).all())

    all_events = [*stocks, *events]
    all_events.sort(key=sort_events)

    cumulated_quantity = 0
    cumulated_buy_value = Decimal(0)
    cumulated_received_value = Decimal(0)
    
    ids = []
    for event in all_events:
        result = create_time_series(
            event,
            cumulated_quantity,
            cumulated_buy_value,
            cumulated_received_value,
        )
        obj, cumulated_quantity, cumulated_buy_value, cumulated_received_value = result
        ids.append(obj.pk)

    today = timezone.now().date()
    if not StockTimeSeries.objects.filter(ticker=ticker, date=today).exists():
        obj = StockTimeSeries.objects.create(
            ticker=ticker,
            date=today,
            quantity=0,
            cumulated_quantity=cumulated_quantity,
            buy_value=0,
            cumulated_buy_value=cumulated_buy_value,
            received_value=0,
            cumulated_received_value=cumulated_received_value,
        )
        ids.append(obj.pk)

    StockTimeSeries.objects.filter(
        ticker=ticker
    ).exclude(
        pk__in=ids
    ).delete()
