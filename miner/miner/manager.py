import json, os, signal, subprocess, time
from pathlib import Path
import psutil

from config import XMRIG_PATH, MINING_STATE, CPU_PERCENT, DATA_DIR, get_default_wallet
from .coins import get_coin

class XMRigManager:
    def __init__(self):
        self.state_file = MINING_STATE
        self.log_file = DATA_DIR / "xmrig.log"

    def _load(self):
        if self.state_file.exists():
            try: return json.loads(self.state_file.read_text())
            except Exception: pass
        return {"running": False, "pid": None, "coin": None, "pool": None, "wallet": None}

    def _save(self, st):
        self.state_file.write_text(json.dumps(st, indent=2))

    def _alive(self, pid):
        if not pid: return False
        try:
            p = psutil.Process(pid)
            return p.is_running() and "xmrig" in p.name().lower()
        except Exception:
            return False

    def status(self):
        st = self._load()
        if st["running"] and not self._alive(st["pid"]):
            st["running"] = False
            self._save(st)
        return st

    def start(self, coin_code, wallet, pool_url, cpu_hint=None):
        if self.status()["running"]:
            return False, "در حال اجراست"

        coin = get_coin(coin_code)
        if not coin: return False, "ارز نامعتبر"

        if not os.path.exists(XMRIG_PATH):
            return False, f"XMRig پیدا نشد: {XMRIG_PATH}"

        wallet = wallet or get_default_wallet(coin_code)
        if not wallet:
            return False, "ولت تنظیم نشده"

        hint = cpu_hint if cpu_hint and 1 <= cpu_hint <= 100 else CPU_PERCENT
        cfg = self._build_config(coin_code, wallet, pool_url, hint)
        cfg_path = DATA_DIR / "xmrig_config.json"
        cfg_path.write_text(json.dumps(cfg, indent=2))

        try:
            self.log_file.parent.mkdir(exist_ok=True)
            log_f = open(self.log_file, "a")
            log_f.write(f"\n\n=== START {time.ctime()} | {coin_code} | {pool_url} | CPU={hint}% ===\n")
            proc = subprocess.Popen(
                [XMRIG_PATH, "-c", str(cfg_path)],
                stdout=log_f, stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        except Exception as e:
            return False, f"خطا در اجرا: {e}"

        time.sleep(2)
        if proc.poll() is not None:
            return False, "XMRig بسته شد — لاگ رو ببین"

        self._save({
            "running": True, "pid": proc.pid,
            "coin": coin_code, "pool": pool_url, "wallet": wallet,
            "started_at": time.time(), "cpu_hint": hint,
        })
        return True, f"شروع شد با {hint}٪ CPU"

    def stop(self):
        st = self.status()
        if not st["running"]: return False, "در حال اجرا نیست"
        try:
            p = psutil.Process(st["pid"])
            for c in p.children(recursive=True): c.terminate()
            p.terminate(); p.wait(timeout=5)
        except Exception:
            try: os.kill(st["pid"], signal.SIGKILL)
            except Exception: pass
        st["running"] = False; st["pid"] = None
        self._save(st)
        return True, "متوقف شد"

    def _build_config(self, coin_code, wallet, pool_url, hint):
        host, port = pool_url.rsplit(":", 1)
        return {
            "api": {"id": None, "worker-id": "myrig"},
            "http": {
                "enabled": True, "host": "127.0.0.1",
                "port": 8080, "access-token": None, "restricted": True,
            },
            "autosave": True,
            "background": False,
            "colors": True,
            "title": True,
            "randomx": {"init": -1, "mode": "auto"},
            "cpu": {
                "enabled": True,
                "huge-pages": True,
                "priority": 2,
                "memory-pool": False,
                "yield": True,                 # 👈 برای اینکه سیستم رو نکشه
                "max-threads-hint": hint,      # 👈 ۳۰٪
                "asm": True,
            },
            "opencl": {"enabled": False},
            "cuda": {"enabled": False},
            "donate-level": 1,
            "log-file": None,
            "pools": [{
                "algo": None,
                "coin": coin_code.lower() if coin_code != "BTC" else None,
                "url": f"{host}:{port}",
                "user": wallet,
                "pass": "x",
                "rig-id": None,
                "nicehash": False,
                "keepalive": True,
                "enabled": True,
                "tls": port == "443",
                "daemon": False,
            }],
            "retries": 5,
            "retry-pause": 5,
            "print-time": 60,
            "dns": {"ipv6": False, "ttl": 30},
            "watch": True,
            "pause-on-battery": True,   # 👈 وقتی لپ‌تاپ رو باتری بود، متوقف
            "pause-on-active": False,
        }

    def stats(self):
        import urllib.request
        try:
            with urllib.request.urlopen("http://127.0.0.1:8080/2/summary", timeout=2) as r:
                d = json.loads(r.read())
            return {
                "hashrate": d.get("hashrate", {}).get("total", [0])[0] or 0,
                "shares_good": d.get("results", {}).get("shares_good", 0),
                "shares_total": d.get("results", {}).get("shares_total", 0),
                "uptime": d.get("connection", {}).get("uptime", 0),
                "pool": d.get("connection", {}).get("pool", ""),
            }
        except Exception:
            return {"hashrate": 0, "shares_good": 0, "shares_total": 0, "uptime": 0, "pool": ""}

    def cpu_usage(self):
        return psutil.cpu_percent(interval=0.5)
