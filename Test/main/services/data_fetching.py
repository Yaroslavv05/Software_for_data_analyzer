import yfinance as yf
from binance.client import Client


class DataFetchingService:
    """
    Only staff related to getting data from other sources
    like binance, yahoofinance, poligon.
    """

    def __init__(self) -> None:
        self.client = Client()
        self.yahoo_finance = yf

    def get_minute_interval(
        self, symbol, exchange, open_price, bound_up, bound_low, date, time_frame
    ):
        exchange_handlers = {
            "Binance": self.handle_binance,
            "YahooFinance": self.handle_yahoo_finance,
            "Poligon": self.handle_polygon,
        }

        # Get the handler function based on the exchange
        handler = exchange_handlers.get(exchange)

        if handler:
            # Call the handler function
            try:
                handler(
                    symbol, exchange, open_price, bound_up, bound_low, date, time_frame
                )
            except Exception as e:
                print(f"An error occurred while processing {exchange} data: {e}")
        else:
            print(f"Unsupported exchange: {exchange}")

    def handle_binance(
        self, symbol, exchange, open_price, bound_up, bound_low, date, time_frame
    ):
        # Fetch Binance-specific data
        # For example:
        # data = self.client.get_klines(symbol=symbol, interval=time_frame)
        # Perform processing if needed
        # ...
        pass

    def handle_yahoo_finance(
        self, symbol, exchange, open_price, bound_up, bound_low, date, time_frame
    ):
        # Fetch Yahoo Finance-specific data
        # For example:
        # data = self.yahoo_finance.download(symbol, start=date, end=date)
        # Perform processing if needed
        # ...
        pass

    def handle_polygon(
        self, symbol, exchange, open_price, bound_up, bound_low, date, time_frame
    ):
        # Fetch Polygon-specific data
        # Perform processing if needed
        # ...
        pass
