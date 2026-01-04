# Orange Pi Wi-Fi Setup Portal

Production-ready Wi-Fi setup portal for **Orange Pi Zero 3**  
(Flask + Gunicorn + NetworkManager)

Проєкт дозволяє:
- автоматично підключатися до відомої Wi-Fi мережі (STA)
- піднімати **AP fallback** при відсутності інтернету
- надавати **captive portal** для налаштування Wi-Fi через браузер
- працювати стабільно після reboot та збоїв мережі

---

## ✨ Функціонал

- 📡 Сканування Wi-Fi мереж (nmcli)
- 🔐 Підключення до вибраної мережі + збереження
- 🔁 Автоматичне перепідключення
- 🚨 AP fallback при помилці або відсутності Wi-Fi
- 🌙 Dark mode
- 📱 Mobile-first UI
- 🔄 Автооновлення списку мереж
- ⚙️ systemd + Gunicorn (production)
- 🧠 Watchdog і state-логіка

---

## 🧱 Архітектура

STA (Wi-Fi клієнт)
│
├─ OK → AP вимкнено
│
└─ FAIL → AP fallback
└─ Captive portal (Flask)

## 📂 Структура проєкту

wifi-setup/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│ └── index.html
├── static/
│ └── (css/js якщо потрібно)
├── venv/
└── systemd/
├── wifi-setup.service
├── wifi-fallback.service
└── wifi-fallback.timer

Системні скрипти:

/usr/local/bin/wifi-state.sh
/usr/local/bin/wifi-fallback.sh

## ⚙️ Вимоги

- Orange Pi Zero 3
- Ubuntu 24.04 (Noble)
- Python 3.12
- NetworkManager
- nmcli

---

## 🚀 Встановлення

git clone <repo>
cd wifi-setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


Запуск (production)

sudo systemctl enable --now wifi-setup.service


Перевірка:

systemctl status wifi-setup.service

🧪 Тестування fallback

неправильний пароль Wi-Fi

вимкнений роутер

reboot без мережі

Очікувано:

зʼявляється AP OrangePi-Setup

IP: 192.168.12.1

відкривається портал

🔐 Безпека

портал доступний тільки з AP

nmcli виконується від root

без відкритих shell-команд

📌 Статус

✔ Production-ready
✔ Embedded / headless
✔ Без ручного втручання

📜 Ліцензія

# Orange Pi Zero 3 – Wi‑Fi Setup Portal (STA only)

## 📌 Опис проєкту

Цей проєкт реалізує **веб‑інтерфейс для налаштування Wi‑Fi** на **Orange Pi Zero 3** під керуванням **Ubuntu 24.04 (Orange Pi 1.0.6 Noble)**.

Пристрій:

* підключається до роутера як **Wi‑Fi клієнт (STA)**
* **сканує доступні Wi‑Fi мережі**
* дозволяє **обрати SSID, ввести пароль**
* підключається через **NetworkManager**
* **запамʼятовує мережу** (persist через NM)
* керується через **веб‑сторінку в браузері**

⚠️ **AP / Hotspot / Fallback режим свідомо ВИКЛЮЧЕНИЙ**

> Вбудований Wi‑Fi чип Orange Pi Zero 3 **не підтримує AP режим на рівні драйвера** (підтверджено через `iw`).

---

## 🧱 Система

```text
OS: Orange Pi Ubuntu 1.0.6 Noble
Distributor ID: Ubuntu
Release: 24.04
Kernel: vendor (Realtek Wi‑Fi)
```

---

## 🧩 Архітектура

```text
Browser
  │
  ▼
Flask Web UI  (Gunicorn)
  │
  ▼
subprocess → nmcli
  │
  ▼
NetworkManager → wlan0 (STA)
```

---

## 📁 Структура проєкту

```text
wifi-setup/
├── app.py                # Flask application
├── templates/
│   └── index.html        # UI (dark, mobile-first)
├── static/
│   └── style.css
├── requirements.txt
├── gunicorn.conf.py
├── wifi-state.sh         # перевірка стану Wi‑Fi
├── systemd/
│   └── wifi-setup.service
└── README.md
```

---

## 🧪 ЕТАП 1. Перевірка системи

```bash
ip link
nmcli device
rfkill list
systemctl status NetworkManager
```

Очікувано:

* `wlan0` існує
* NetworkManager `active (running)`

---

## 🧪 ЕТАП 2. Python середовище

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

cd ~/wifi-setup
python3 -m venv venv
source venv/bin/activate
```

---

## 🧪 ЕТАП 3. Flask застосунок

### `app.py`

```python
from flask import Flask, request, jsonify, render_template
import subprocess

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scan")
def scan():
    result = subprocess.run(
        ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "device", "wifi", "list"],
        capture_output=True,
        text=True
    )

    networks = []
    for line in result.stdout.splitlines():
        inuse, ssid, signal, sec = line.split(":", 3)
        if ssid:
            networks.append({
                "ssid": ssid,
                "signal": signal,
                "security": sec,
                "inuse": inuse == "*"
            })

    return jsonify(networks)

@app.route("/connect", methods=["POST"])
def connect():
    ssid = request.form.get("ssid")
    password = request.form.get("password")

    cmd = ["nmcli", "device", "wifi", "connect", ssid]
    if password:
        cmd += ["password", password]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return "OK"
    return result.stderr, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

---

## 🧪 ЕТАП 4. UI (dark + mobile-first)

Функціонал:

* кнопка **Scan Wi‑Fi**
* автооновлення списку
* відображення рівня сигналу
* форма підключення

(HTML/CSS стандартний, без JS‑фреймворків)

---

## 🧪 ЕТАП 5. requirements.txt

```text
Flask==3.0.0
Gunicorn==21.2.0
```

Оновлення:

```bash
pip freeze > requirements.txt
```

---

## 🧪 ЕТАП 6. Gunicorn

### `gunicorn.conf.py`

```python
bind = "0.0.0.0:8080"
workers = 1
timeout = 30
```

Запуск вручну:

```bash
gunicorn -c gunicorn.conf.py app:app
```

---

## 🧪 ЕТАП 7. systemd сервіс

### `systemd/wifi-setup.service`

```ini
[Unit]
Description=Orange Pi WiFi Setup Portal
After=network.target NetworkManager.service

[Service]
User=root
WorkingDirectory=/home/yoghurt/wifi-setup
ExecStart=/home/yoghurt/wifi-setup/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Установка:

```bash
sudo cp systemd/wifi-setup.service /etc/systemd/system/
sudo systemctl daemon-reexec
sudo systemctl enable wifi-setup
sudo systemctl start wifi-setup
```

---

## 🧪 ЕТАП 8. Перевірка

```bash
systemctl status wifi-setup
ss -tulpn | grep 8080
```

У браузері:

```
http://<IP>:8080
```

---

## ⚠️ Обмеження (ВАЖЛИВО)

* ❌ AP / Hotspot / Fallback **НЕ підтримується** вбудованим Wi‑Fi
* ❌ `iw dev wlan0 set type __ap` → `Input/output error (-5)`
* ❌ `nmcli hotspot` працює псевдо

✔ Підтримується **тільки STA (клієнт)**

---

## ✅ Результат

✔ Web‑портал налаштування Wi‑Fi
✔ Persist конфігурації через NetworkManager
✔ Gunicorn + systemd
✔ Готово до продакшну

---

## 🔜 Можливі покращення

* USB Wi‑Fi адаптер для AP fallback
* Captive portal
* API для Home Assistant
* Docker (за потреби)

---

**Автор:** Orange Pi Zero 3 Wi‑Fi Setup Project


