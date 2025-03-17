from django.utils import timezone
from decimal import Decimal
from domains.tickers.models import Ticker, TickerPrice
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
    current_price: Decimal,
):
    if isinstance(instance, TradingStock):
        date = instance.trading_note.trading_date
        quantity = instance.quantity
        buy_value = instance.unit_price * quantity

        average_cost = buy_value / quantity
        if buy_value == 0:
            average_cost = cumulated_buy_value / cumulated_quantity

        if instance.trading_type == TradingStock.TYPE_BUY:
            new_quantity = cumulated_quantity + quantity
            new_buy_value = cumulated_buy_value + buy_value
        else:
            new_quantity = cumulated_quantity - quantity
            new_buy_value = cumulated_buy_value - buy_value

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
                'average_cost': average_cost,
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
            'average_cost': current_price,
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

    current_price = 0
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
            current_price,
        )
        obj, cumulated_quantity, cumulated_buy_value, cumulated_received_value = result
        current_price = obj.average_cost
        ids.append(obj.pk)

    StockTimeSeries.objects.filter(
        ticker=ticker
    ).exclude(
        pk__in=ids
    ).delete()

    today = timezone.now().date()
    if not StockTimeSeries.objects.filter(ticker=ticker, date=today).exists():
        ticker_price = TickerPrice.objects.filter(ticker=ticker).order_by('-date_time').first()
        if ticker_price:
            obj = StockTimeSeries.objects.update_or_create(
                ticker=ticker,
                date=today,
                defaults={
                    'quantity': 0,
                    'cumulated_quantity': cumulated_quantity,
                    'buy_value': 0,
                    'cumulated_buy_value': cumulated_buy_value,
                    'received_value': 0,
                    'cumulated_received_value': cumulated_received_value,
                    'average_cost': ticker_price.price,
                },
            )
