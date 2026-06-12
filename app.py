from flask import Flask, render_template, request, jsonify, session
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "otpdoctor-secret-2026")

BASE_URL = "https://otpdoctor.in/stubs/handler_api.php"

def api_call(params):
    try:
        r = requests.get(BASE_URL, params=params, timeout=15)
        r.raise_for_status()
        # Try JSON first
        try:
            return {"ok": True, "data": r.json()}
        except Exception:
            return {"ok": True, "raw": r.text}
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        return {"ok": False, "error": str(e)}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/balance")
def balance():
    key = request.args.get("api_key", "")
    if not key:
        return jsonify({"ok": False, "error": "No API key"})
    result = api_call({"action": "getBalance", "api_key": key})
    return jsonify(result)


@app.route("/api/countries")
def countries():
    key = request.args.get("api_key", "")
    result = api_call({"action": "getCountries", "api_key": key})
    return jsonify(result)


@app.route("/api/services")
def services():
    key = request.args.get("api_key", "")
    country = request.args.get("country", "in")
    result = api_call({"action": "getServices", "api_key": key, "country": country})
    return jsonify(result)


@app.route("/api/buy")
def buy():
    key = request.args.get("api_key", "")
    service = request.args.get("service", "")
    max_price = request.args.get("maxPrice", "")
    params = {"action": "getNumber", "api_key": key, "service": service}
    if max_price:
        params["maxPrice"] = max_price
    result = api_call(params)
    return jsonify(result)


@app.route("/api/status")
def check_status():
    key = request.args.get("api_key", "")
    activation_id = request.args.get("id", "")
    result = api_call({"action": "getStatus", "api_key": key, "id": activation_id})
    return jsonify(result)


@app.route("/api/set_status")
def set_status():
    key = request.args.get("api_key", "")
    activation_id = request.args.get("id", "")
    status = request.args.get("status", "")
    result = api_call({"action": "setStatus", "api_key": key, "id": activation_id, "status": status})
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
