from procrastinate.contrib.django import app
from .compute import compute

@app.periodic(cron="*/1 * * * *", queue="stocks")
@app.task
def defer_compute_all_time_series(timestamp: int):
    print("COMPUTING_TIME_SERIES")
    from domains.tickers.models import Ticker
    tickers = Ticker.objects.all()
    for t in tickers:
        compute_time_series.defer(ticker_name=t.code)

@app.task(queue='stocks')
def compute_time_series(ticker_name: str):
    print(f"COMPUTING_TIME_SERIES FOR {ticker_name}")

    from domains.tickers.models import Ticker
    ticker = Ticker.objects.get(code=ticker_name)

    compute(ticker)
