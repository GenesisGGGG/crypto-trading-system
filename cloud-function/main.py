import ccxt
import config

coinbase = ccxt.coinbase({
    'apiKey': config.API_KEY,
    'secret': config.API_SECRET, 
    'createMarketBuyOrderRequiresPrice': False,
    'verbose': True
})

def cancel_all_orders_for_ticker(ticker):
    try:
        # Fetch all open orders (on Coinbase)
        open_orders = coinbase.fetch_open_orders()

        # Filter orders by the ticker symbol
        orders_to_cancel = [order for order in open_orders if order['symbol'] == ticker]

        # Cancel each order
        for order in orders_to_cancel:
            print(f"Cancelling order: {order['id']}")
            coinbase.cancel_order(order['id'])
            
        return {"code": "success", "message": f"All orders for {ticker} have been cancelled."}

    except ccxt.BaseError as e:
        print(f"Error: {e}")
        return {"code": "error", "message": str(e)}

def trade_crypto(request):
    data = request.get_json()
    if 'passphrase' not in data or data['passphrase'] != config.PASSPHRASE_TRADINGVIEW: 
        return {
            "code": "error", 
            "message": "invalid passphrase, forbidden"
        }
    
    tickers = {
        'ADAETH': 'ADA/ETH',
        'NEARUSD': 'NEAR/USD',
        'MATICUSD': 'POL/USD', 
        'VETUSD': 'VET/USD',
        'ONDOUSD': 'ONDO/USD',
        'INJUSD': 'INJ/USD'
    }
    ticker = tickers[data['ticker']]
    balance = coinbase.fetch_balance()
    crypto_symbol = ticker.split('/')[0]    
    usd_balance = balance['total'].get('USD', 0)
    price = float(data['close'])
    amountUSD = float(data['amountUSD'])
    
    
    if data['type'] == 'buy': 

        open_orders = coinbase.fetch_open_orders()
        outstanding_orders = [order for order in open_orders if order['symbol'] == ticker]

        if outstanding_orders:
            print(f"Outstanding orders exist for {ticker}. Skipping buy.")
            return {"code": "info", "message": f"Outstanding orders exist for {ticker}. No new buy order created."}
        else:
            order_book = coinbase.fetch_order_book(ticker)
            bid_price = order_book['bids'][0][0]
            coinbase.create_market_buy_order_with_cost(ticker, amountUSD/bid_price)
        
    if data['type'] == 'sell':
        cancel_all_orders_for_ticker(ticker)
        crypto_balance = balance['total'].get(crypto_symbol, 0)
        order_book = coinbase.fetch_order_book(ticker)
        order = coinbase.create_market_sell_order_wi(ticker, crypto_balance/2)
        
    
    return order