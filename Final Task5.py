from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

def calculate_intraday_pl(stock_name, start_date, end_date, entry_time, exit_time):
    # Download 1-minute data (last 7 days)
    df = yf.download(stock_name, interval="1m", period="7d")
    df.index = df.index.tz_localize(None)
    df = df.loc[start_date:end_date]

    if df.empty:
        return None, "No data available for given date range"

    # Flatten columns if MultiIndex
    df.columns = df.columns.get_level_values(0)
    df["Date"] = df.index.date
    df["Time"] = df.index.time

    results = []
    entry_dt = pd.to_datetime(entry_time).time()
    exit_dt = pd.to_datetime(exit_time).time()

    for d in sorted(df["Date"].unique()):
        day_data = df[df["Date"] == d]

        entry_rows = day_data[day_data["Time"] <= entry_dt]
        exit_rows = day_data[day_data["Time"] <= exit_dt]

        if entry_rows.empty or exit_rows.empty:
            continue

        entry_row = entry_rows.iloc[-1]
        exit_row = exit_rows.iloc[-1]

        buy_price = float(entry_row["Close"])
        sell_price = float(exit_row["Close"])
        pnl = sell_price - buy_price

        results.append({
            "Date": str(d),
            "BuyPrice": round(buy_price, 4),
            "SellPrice": round(sell_price, 4),
            "PnL": round(pnl, 4)
        })

    if not results:
        return [], "No trades found"

    overall_pl = round(sum([r["PnL"] for r in results]), 4)
    return {"daily_pl": results, "overall_pl": overall_pl}, None

@app.route('/intraday_pl', methods=['GET', 'POST'])
def intraday_pl():
    try:
        if request.method == "POST":
            data = request.get_json()
            stock_name = data.get("stock_name")
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            entry_time = data.get("entry_time")
            exit_time = data.get("exit_time")
        else:  # GET method
            stock_name = request.args.get("stock_name")
            start_date = request.args.get("start_date")
            end_date = request.args.get("end_date")
            entry_time = request.args.get("entry_time")
            exit_time = request.args.get("exit_time")

        if not all([stock_name, start_date, end_date, entry_time, exit_time]):
            return jsonify({"error": "Missing required parameters"}), 400

        result, error = calculate_intraday_pl(stock_name, start_date, end_date, entry_time, exit_time)
        if error:
            return jsonify({"error": error}), 400 if result is None else 200

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5005)
