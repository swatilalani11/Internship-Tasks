from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    # For POST, try to get JSON, if none just ignore
    data = request.get_json(silent=True)
    response = {"message": "Hello, World!"}
    if data:
        response["your_data"] = data
    return jsonify(response)

@app.route("/test", methods=["GET", "POST"])
def test():
    data = request.get_json(silent=True)
    response = {"message": "This is a test page."}
    if data:
        response["your_data"] = data
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, port=5002)
