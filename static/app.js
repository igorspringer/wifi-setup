  let autoScanTimer = null;

  function signalIcon(level) {
    if (level > 80) return "▂▄▆█";
    if (level > 60) return "▂▄▆";
    if (level > 40) return "▂▄";
    return "▂";
  }

  function scanWifi() {
    fetch("/scan")
      .then(r => r.json())
      .then(data => {
        const list = document.getElementById("wifi-list");
        list.innerHTML = "";

        data.forEach(net => {
          const li = document.createElement("li");
          if (net.in_use) li.classList.add("active");

          li.onclick = () => {
            document.getElementById("ssid").value = net.ssid;
          };

          li.innerHTML = `
            <div>
              <div class="ssid">
                ${net.ssid}
                ${net.secure ? "🔒" : ""}
                ${net.in_use ? " ⭐" : ""}
              </div>
              <div class="meta">${net.signal}%</div>
            </div>
            <div class="signal">${signalIcon(net.signal)}</div>
          `;

          list.appendChild(li);
        });
      });
  }

  /* 🔄 автооновлення кожні 10 секунд */
  function startAutoScan() {
    scanWifi();
    autoScanTimer = setInterval(scanWifi, 10000);
  }

  window.onload = startAutoScan;


const ipInput = document.getElementById("ip");
const gatewayInput = document.getElementById("gateway");
const dnsInput = document.getElementById("dns");
const button = document.getElementById("apply-static-ip");
const error = document.getElementById("ip-error");

function isValidIP(ip) {
  const regex =
    /^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/;
  return regex.test(ip);
}

function validateForm() {
  error.classList.add("hidden");
  error.textContent = "";

  if (!isValidIP(ipInput.value)) {
    error.textContent = "Невірний IP адрес";
  } else if (!isValidIP(gatewayInput.value)) {
    error.textContent = "Невірний Gateway";
  } else if (dnsInput.value && !isValidIP(dnsInput.value)) {
    error.textContent = "Невірний DNS";
  }

  if (error.textContent) {
    error.classList.remove("hidden");
    button.disabled = true;
    return;
  }

  button.disabled = false;
}

[ipInput, gatewayInput, dnsInput].forEach(input =>
  input.addEventListener("input", validateForm)
);

document
  .getElementById("static-ip-form")
  .addEventListener("submit", async e => {
    e.preventDefault();

    const payload = {
      ip: ipInput.value,
      gateway: gatewayInput.value,
      dns: dnsInput.value || "8.8.8.8"
    };

    console.log("STATIC IP PAYLOAD:", payload);

    document.getElementById("net-status").innerText =
      "Застосування статичного IP...";

    try {
      const res = await fetch("/set-static-ip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      document.getElementById("net-status").innerText =
        data.message || data.error;

    } catch (err) {
      document.getElementById("net-status").innerText =
        "Помилка зʼєднання з сервером";
    }
  });


  document.getElementById("dhcp-btn").onclick = async () => {
  document.getElementById("dhcp-status").innerText = "Застосування DHCP...";
  try {
    const r = await fetch("/set_dhcp", { method: "POST" });
    const d = await r.json();
    document.getElementById("dhcp-status").innerText = d.message;
  } catch {
    document.getElementById("dhcp-status").innerText = "Помилка запиту";
  }
};


  async function loadNetStatus() {
    try {
      const r = await fetch("/network_status");
      const d = await r.json();

      document.getElementById("cur-ip").innerText = d.ip || "—";
      document.getElementById("cur-gw").innerText = d.gateway || "—";
      document.getElementById("cur-dns").innerText = d.dns || "—";
    } catch {
      document.getElementById("cur-ip").innerText = "error";
    }
  }

  loadNetStatus();
  setInterval(loadNetStatus, 5000);
