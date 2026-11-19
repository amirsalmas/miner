const $ = s => document.querySelector(s);
const COINS = window.__COINS__, WALLETS = window.__WALLETS__;
const coinSel = $("#coin-select"), poolSel = $("#pool-select");
const walletIn = $("#wallet-input");

function fillPools(code) {
  const coin = COINS.find(c => c.code === code);
  poolSel.innerHTML = "";
  coin.pools.forEach(p => {
    const o = document.createElement("option");
    o.value = p.url; o.textContent = `${p.name} — ${p.url}`;
    poolSel.appendChild(o);
  });
  walletIn.value = WALLETS[code] || "";
  const note = $("#coin-note");
  if (coin.note) { note.textContent = "⚠️ " + coin.note; note.style.display = "block"; }
  else note.style.display = "none";
}

coinSel.addEventListener("change", () => fillPools(coinSel.value));
$("#cpu-slider").addEventListener("input", e => {
  $("#cpu-val").textContent = e.target.value + "٪";
  $("#cpu-badge").textContent = e.target.value + "٪ CPU";
});

$("#btn-save-wallet").addEventListener("click", async () => {
  const r = await fetch("/api/wallets", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ coin: coinSel.value, address: walletIn.value.trim() })
  });
  const d = await r.json();
  $("#wallet-msg").textContent = d.ok ? "✅ ذخیره شد" : "❌ " + d.error;
  if (d.ok) WALLETS[coinSel.value] = walletIn.value.trim();
});

$("#btn-start").addEventListener("click", async () => {
  $("#msg").textContent = "در حال شروع…";
  const r = await fetch("/api/mining/start", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      coin: coinSel.value, pool: poolSel.value,
      wallet: walletIn.value.trim(),
      cpu_hint: parseInt($("#cpu-slider").value)
    })
  });
  const d = await r.json();
  $("#msg").textContent = d.ok ? "✅ " + d.message : "❌ " + (d.error || d.message);
  refresh();
});

$("#btn-stop").addEventListener("click", async () => {
  const r = await fetch("/api/mining/stop", { method: "POST" });
  const d = await r.json();
  $("#msg").textContent = d.ok ? "⏸ " + d.message : "❌ " + d.message;
  refresh();
});

async function refresh() {
  try {
    const st = await fetch("/api/status").then(r => r.json());
    $("#s-running").textContent = st.running ? `✅ ${st.coin}` : "⏸ متوقف";
    $("#s-running").className = st.running ? "ok" : "";
    $("#s-hashrate").textContent = `${(st.stats?.hashrate || 0).toFixed(1)} H/s`;
    $("#s-good").textContent = st.stats?.shares_good ?? 0;
    const up = st.stats?.uptime || 0;
    $("#s-uptime").textContent = up > 0
      ? `${Math.floor(up/3600)}h ${Math.floor((up%3600)/60)}m` : "—";
    $("#s-cpu").textContent = (st.cpu_percent || 0).toFixed(0) + "%";
    $("#s-mem").textContent = (st.mem_percent || 0).toFixed(0) + "%";
    $("#cpu-meter").style.width = (st.cpu_percent || 0) + "%";
  } catch {}
}

fillPools(coinSel.value);
refresh();
setInterval(refresh, 4000);
