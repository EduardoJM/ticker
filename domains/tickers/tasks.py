from procrastinate.contrib.django import app

@app.periodic(cron="*/15 * * * *", queue="tickers")
@app.task
def defer_fetch_all_tickers_price(timestamp: int):
    print("FETCHING TICKERS PRICE")
    from .models import Ticker
    tickers = Ticker.objects.all()
    for t in tickers:
        fetch_ticker_price.defer(ticker_name=t.code)

@app.task(queue='tickers')
def fetch_ticker_price(ticker_name: str):
    import yfinance as yf
    from .models import Ticker, TickerPrice
    
    ticker = Ticker.objects.get(code=ticker_name)

    yf_ticker = yf.Ticker(f"{ticker_name}.SA")
    yf_info = yf_ticker.info
    price = yf_info.get('regularMarketPrice')
    if not price:
        raise Exception('TODO: enchance this')
    
    TickerPrice.objects.create(
        ticker=ticker,
        price=price,
    )
