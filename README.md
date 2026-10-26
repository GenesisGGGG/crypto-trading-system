# crypto-trading-system

Automated crypto trading system I built and ran live, split into the two halves that actually move money:

- **`tradingview/`** — 22 Pine Script indicators & strategies that generate the signals
- **`cloud-function/`** — the Google Cloud Function that receives webhooks and executes orders on Coinbase Advanced Trade (via `ccxt`)

Signal flow: **TradingView strategy → webhook POST → Cloud Function → Coinbase.**

## Architecture

```
TradingView (Pine strategies, this repo's tradingview/ folder)
        │  alert fires: webhook POST {ticker, close, amountUSD, type, passphrase}
        ▼
Google Cloud Function  (cloud-function/)  ── passphrase gate · ticker mapping · order dedup
        │  ccxt → Coinbase Advanced Trade REST
        ▼
Coinbase  ── market buys sized in USD · half-position sells
```

## tradingview/

22 Pine Script studies — RSI/MACD crossover signals, extreme-candle reversal strategies (1D/4H), RSI divergence (v6), slope detectors, stop-loss indicators, and the composite `Custom Trading Bot Strategy` that wires signals to a webhook URL. Code is kept exactly as saved in TradingView. `backtests/` holds the start of a vectorbt BTC validation notebook.

## cloud-function/

- `main.py` — HTTP-triggered `trade_crypto(request)`: passphrase auth, TradingView→ccxt ticker mapping, order-deduplication on buys (skips if open orders exist), cancels + half-sell on sell signals
- `config.py.example` — Coinbase CDP key + EC private key + webhook passphrase template (`config.py` is gitignored)
- `sample-alert-payload.json` — the alert shape TradingView sends
- `local-test-stub.py` — earliest iteration of the endpoint

## Setup

1. **Coinbase** — create a Coinbase Developer Platform API key (Advanced Trade), download the EC private key.
2. **Config** —
   ```bash
   cp cloud-function/config.py.example cloud-function/config.py   # fill in keys
   ```
3. **Deploy** — `gcloud functions deploy trade_crypto --trigger-http --runtime=python312`
4. **TradingView** — attach the function URL as a webhook in the alert, payload shaped like `sample-alert-payload.json`.

Use least-privilege keys (trade-only, no withdrawals) and a strong webhook passphrase.

## Status

Decommissioned after a long live run — the autonomous/bot lane was shut down in favor of discretionary trading. Kept as the working artifact: signals, execution, and the honest rough edges.

## Known issues (as deployed)

- Sell path has a typo'd ccxt call (`create_market_sell_order_wi`) that would raise at runtime — caught in the decommission review.
- No retry/error handling around exchange calls.
- Ticker map hardcoded; new pairs require edit + redeploy.

## Stack

Pine Script v5/v6 · Python · ccxt · Coinbase Advanced Trade · Google Cloud Functions · TradingView webhooks · vectorbt
