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

