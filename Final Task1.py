from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

@app.route('/download_stock', methods=['GET', 'POST'])
def download_stock():
    try:
        # Get input from POST JSON or GET query parameters
        if request.method == 'POST':
            data = request.get_json()
            symbol = data.get('symbol')
            start = data.get('start_date')
            end = data.get('end_date')
            interval = data.get('timeframe', '1d')
        else:  # GET
            symbol = request.args.get('symbol')
            start = request.args.get('start_date')
            end = request.args.get('end_date')
            interval = request.args.get('timeframe', '1d')

        # Validate inputs
        if not symbol or not start or not end:
            return jsonify({"error": "Please provide 'symbol', 'start_date', and 'end_date'"}), 400

        # Download stock data
        df = yf.download(symbol, start=start, end=end, interval=interval)
        if df.empty:
            return jsonify({"error": "No data found for this symbol or date range"}), 400

        # Format data
        df.reset_index(inplace=True)
        df['date'] = df['Date'].dt.date.astype(str)
        df['time'] = df['Date'].dt.time.astype(str)
        df = df[['date','time','Open','High','Low','Close','Volume']]
        df.columns = ['date','time','open','high','low','close','volume']

        return jsonify(df.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({"message": "API is running! Use GET or POST /download_stock with parameters."})

if __name__ == "__main__":
    app.run(debug=True, port=5004)
