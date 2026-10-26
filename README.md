# crypto-trading-system

Automated crypto trading system I built and ran live, split into the two halves that actually move money:

- **`tradingview/`** — the Pine Script side: 8 backtestable strategies plus the companion signal/alert/stop indicators that feed them
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

Not 22 standalone bots — the pines are a few signal families, each a backtestable `strategy()` with its companion `indicator()` studies layered on top:

- **RSI/MACD crossover systems** — `40 RSI-MACD`, `RSI Under 40 and MACD Crossover Buy Signal`, `RSI Over 60 and MACD Crossover Sell Signal`, `RSI and MACD Buy Signal (Nested)`, `RSI and MACD Sell Signal (Bullish-Sharp Recovery)`, `Sell (RSI & MACD)`
- **Extreme-candle reversal family** — `V1 - Extreme Candle Reversal Strategy (1D)` and `(4H)` (+ the BTC-specific 1D variant), each with its alert-indicator companions
- **Momentum/RSI variants** — `RSI Divergence Strategy`, `RSI Cross Above EMA`, `RSI with SMA and Crossover Alerts`, `V1 - MACD Histogram Increasing Strategy`
- **Utility indicators** — slope detectors (`RSI EMA Slope`, `RSI with SMA Slope Alert`, `MACD Increasing Detector`), stop-loss levels (`Stop Loss`, `Stop Loss Indicator (8%-5%)`), and `Custom Trading Bot Strategy`, the composite indicator that wires the signals to the webhook URL

Code is kept exactly as saved in TradingView. `backtests/` holds the start of a vectorbt BTC validation notebook.

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
