from flask import Flask, render_template, jsonify, request
import subprocess
import threading
import time
import ipaddress

app = Flask(__name__)

ROLLBACK_TIMEOUT = 60
rollback_timer = None

def set_static_ip(ip, gateway, dns):
    subprocess.run([
        "nmcli", "con", "mod", "netplan-wlan0",
        "ipv4.method", "manual",
        "ipv4.addresses", f"{ip}/24",
        "ipv4.gateway", gateway,
        "ipv4.dns", dns
    ], check=True)

    subprocess.run(["nmcli", "con", "up", "netplan-wlan0"], check=True)

def rollback_to_dhcp():
    subprocess.run([
        "nmcli", "con", "mod", "netplan-wlan0",
        "ipv4.method", "auto"
    ])
    subprocess.run(["nmcli", "con", "up", "netplan-wlan0"])

def start_rollback_timer():
    global rollback_timer

    if rollback_timer:
        rollback_timer.cancel()

    rollback_timer = threading.Timer(ROLLBACK_TIMEOUT, rollback_to_dhcp)
    rollback_timer.start()

def get_active_wifi_connection():
    r = subprocess.check_output(
        ["nmcli", "-t", "-f", "NAME,DEVICE", "con", "show", "--active"],
        text=True
    )
    for line in r.splitlines():
        name, dev = line.split(":")
        if dev == "wlan0":
            return name
    raise RuntimeError("Active Wi-Fi connection not found")

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

@app.route("/set-static-ip", methods=["POST"])
def set_static_ip():
    data = request.get_json(force=True)

    ip = data.get("ip")
    gateway = data.get("gateway")
    dns = data.get("dns")

    # 🔐 базова валідація
    try:
        ipaddress.ip_address(ip)
        ipaddress.ip_address(gateway)
        if dns:
            ipaddress.ip_address(dns)
    except ValueError:
        return jsonify(error="Invalid IP format"), 400

    try:
        conn = get_active_wifi_connection()

        # 1️⃣ встановлюємо static IP
        subprocess.run(
            [
                "nmcli", "con", "mod", conn,
                "ipv4.method", "manual",
                "ipv4.addresses", f"{ip}/24",
                "ipv4.gateway", gateway,
                "ipv4.dns", dns or ""
            ],
            check=True
        )

        # 2️⃣ застосовуємо
        subprocess.run(
            ["nmcli", "con", "down", conn],
            check=True
        )
        subprocess.run(
            ["nmcli", "con", "up", conn],
            check=True
        )

        return jsonify(message="Статичний IP застосовано"), 200

    except Exception as e:
        return jsonify(error=str(e)), 500

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
