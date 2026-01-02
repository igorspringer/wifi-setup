from flask import Flask, render_template, jsonify
import subprocess
from flask import request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scan")
def scan():
    result = subprocess.run(
        ["/usr/bin/nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "device", "wifi", "list"],
        capture_output=True, text=True
    )

    networks = {}

    for line in result.stdout.strip().split("\n"):
        if not line:
            continue

        in_use, ssid, signal, security = line.split(":", 3)
        if not ssid:
            ssid = "(hidden)"

        signal = int(signal)

        # залишаємо найсильніший сигнал
        if ssid not in networks or networks[ssid]["signal"] < signal:
            networks[ssid] = {
                "ssid": ssid,
                "signal": signal,
                "secure": bool(security),
                "in_use": in_use == "*"
            }

    return jsonify(sorted(networks.values(), key=lambda x: -x["signal"]))

@app.route("/connect", methods=["POST"])
def connect():
    data = request.json
    ssid = data.get("ssid")
    password = data.get("password", "")

    if not ssid:
        return "SSID не заданий", 400

    cmd = [
        "nmcli", "device", "wifi", "connect", ssid
    ]

    if password:
        cmd += ["password", password]

    result = subprocess.run(
        cmd, capture_output=True, text=True
    )

    if result.returncode != 0:
        return f"Помилка:\n{result.stderr}", 500

    return f"Підключено до {ssid}"

if __name__ == "__main__":
    pass
#    app.run(host="0.0.0.0", port=8080)
