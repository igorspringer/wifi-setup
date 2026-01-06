from flask import Flask, render_template, jsonify, request
import subprocess

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

@app.route("/set_static_ip", methods=["POST"])
def set_static_ip():
    try:
        # визначаємо активне Wi-Fi підключення
        con = subprocess.check_output(
            ["nmcli", "-t", "-f", "NAME,DEVICE", "con", "show", "--active"],
            text=True
        )

        wifi_con = None
        for line in con.splitlines():
            name, dev = line.split(":")
            if dev == "wlan0":
                wifi_con = name
                break

        if not wifi_con:
            return {"message": "Активне Wi-Fi підключення не знайдено"}, 400

        # ⚠️ ЗАДАЙ СВОЇ ПАРАМЕТРИ
        STATIC_IP = "10.10.38.50/24"
        GATEWAY = "10.10.38.1"
        DNS = "8.8.8.8 1.1.1.1"

        subprocess.run(
            ["nmcli", "con", "mod", wifi_con,
             "ipv4.method", "manual",
             "ipv4.addresses", STATIC_IP,
             "ipv4.gateway", GATEWAY,
             "ipv4.dns", DNS],
            check=True
        )

        subprocess.run(["nmcli", "con", "down", wifi_con], check=True)
        subprocess.run(["nmcli", "con", "up", wifi_con], check=True)

        return {"message": f"Статичний IP {STATIC_IP} застосовано"}

    except Exception as e:
        return {"message": f"Помилка: {e}"}, 500

@app.route("/set_dhcp", methods=["POST"])
def set_dhcp():
    try:
        conns = subprocess.check_output(
            ["nmcli", "-t", "-f", "NAME,DEVICE", "con", "show", "--active"],
            text=True
        )

        wifi_con = None
        for line in conns.splitlines():
            name, dev = line.split(":")
            if dev == "wlan0":
                wifi_con = name
                break

        if not wifi_con:
            return {"message": "Активне Wi-Fi підключення не знайдено"}, 400

        # 🔑 ВАЖЛИВО: повністю очистити статичні параметри
        subprocess.run(
            [
                "nmcli", "con", "mod", wifi_con,
                "ipv4.method", "auto",
                "ipv4.addresses", "",
                "ipv4.gateway", "",
                "ipv4.dns", ""
            ],
            check=True
        )

        subprocess.run(["nmcli", "con", "down", wifi_con], check=True)
        subprocess.run(["nmcli", "con", "up", wifi_con], check=True)

        return {"message": "DHCP увімкнено. Статичні IP очищено."}

    except Exception as e:
        return {"message": f"Помилка: {e}"}, 500

@app.route("/network_status")
def network_status():
    try:
        out = subprocess.check_output(
            ["nmcli", "-t", "-f", "IP4.ADDRESS,IP4.GATEWAY,IP4.DNS", "device", "show", "wlan0"],
            text=True
        )

        data = {
            "ip": "",
            "gateway": "",
            "dns": ""
        }

        for line in out.splitlines():
            if line.startswith("IP4.ADDRESS"):
                data["ip"] = line.split(":", 1)[1]
            elif line.startswith("IP4.GATEWAY"):
                data["gateway"] = line.split(":", 1)[1]
            elif line.startswith("IP4.DNS"):
                data["dns"] += line.split(":", 1)[1] + " "

        return data

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    pass
#    app.run(host="0.0.0.0", port=80)
