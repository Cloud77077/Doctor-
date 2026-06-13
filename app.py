from flask import Flask, render_template, request, jsonify
import requests
import os
import threading
import time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "otpdoctor-secret-2026")

OTPDOCTOR_BASE = "https://otpdoctor.in/stubs/handler_api.php"
OTPSERVICE_BASE = "https://admin.otpservice.xyz/stubs/handler_api.php"


def api_get(url, params, timeout=15):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        try:
            return {"ok": True, "data": r.json()}
        except Exception:
            return {"ok": True, "raw": r.text.strip()}
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        return {"ok": False, "error": str(e)}


# ── PING (keep-alive) ─────────────────────────────────────────────
@app.route("/ping")
def ping():
    return "ok", 200


# ── MAIN PAGE ─────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ═══════════════════════════════════════════════════════════════════
# OTP DOCTOR ROUTES
# ═══════════════════════════════════════════════════════════════════

@app.route("/od/balance")
def od_balance():
    key = request.args.get("api_key", "")
    return jsonify(api_get(OTPDOCTOR_BASE, {"action": "getBalance", "api_key": key}))


@app.route("/od/countries")
def od_countries():
    key = request.args.get("api_key", "")
    return jsonify(api_get(OTPDOCTOR_BASE, {"action": "getCountries", "api_key": key}))


@app.route("/od/services")
def od_services():
    key = request.args.get("api_key", "")
    country = request.args.get("country", "in")
    return jsonify(api_get(OTPDOCTOR_BASE, {"action": "getServices", "api_key": key, "country": country}))


@app.route("/od/buy")
def od_buy():
    key = request.args.get("api_key", "")
    service = request.args.get("service", "")
    max_price = request.args.get("maxPrice", "")
    params = {"action": "getNumber", "api_key": key, "service": service}
    if max_price:
        params["maxPrice"] = max_price
    return jsonify(api_get(OTPDOCTOR_BASE, params))


@app.route("/od/status")
def od_status():
    key = request.args.get("api_key", "")
    aid = request.args.get("id", "")
    return jsonify(api_get(OTPDOCTOR_BASE, {"action": "getStatus", "api_key": key, "id": aid}))


@app.route("/od/set_status")
def od_set_status():
    key = request.args.get("api_key", "")
    aid = request.args.get("id", "")
    status = request.args.get("status", "")
    return jsonify(api_get(OTPDOCTOR_BASE, {"action": "setStatus", "api_key": key, "id": aid, "status": status}))


# ═══════════════════════════════════════════════════════════════════
# OTP SERVICE ROUTES
# ═══════════════════════════════════════════════════════════════════

@app.route("/os/buy")
def os_buy():
    key = request.args.get("api_key", "")
    service = request.args.get("service", "")
    return jsonify(api_get(OTPSERVICE_BASE, {"action": "getNumber", "api_key": key, "service": service}))


@app.route("/os/otp")
def os_otp():
    key = request.args.get("api_key", "")
    tid = request.args.get("transactionId", "")
    return jsonify(api_get(OTPSERVICE_BASE, {"action": "getOtp", "api_key": key, "transactionId": tid}))


@app.route("/os/cancel")
def os_cancel():
    key = request.args.get("api_key", "")
    tid = request.args.get("transactionId", "")
    return jsonify(api_get(OTPSERVICE_BASE, {"action": "cancelNumber", "api_key": key, "transactionId": tid}))


# ── KEEP-ALIVE THREAD ─────────────────────────────────────────────
def keep_alive():
    time.sleep(30)
    while True:
        try:
            url = os.environ.get("APP_URL", "")
            if url:
                requests.get(url.rstrip("/") + "/ping", timeout=10)
        except Exception:
            pass
        time.sleep(240)


t = threading.Thread(target=keep_alive, daemon=True)
t.start()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
