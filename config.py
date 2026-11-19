import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# 👇 آدرس ولت خودت رو اینجا بذار
# ═══════════════════════════════════════════════════════════════
DEFAULT_WALLET_BTC  = "bc1q3pgr40jxs4ufg4hu9008m20ac5ar6rv96ejmu9"
DEFAULT_WALLET_XMR  = ""  # اگه Monero هم می‌خوای، آدرسش رو بذار
# ═══════════════════════════════════════════════════════════════

DEFAULT_COIN        = "BTC"          # ارز پیش‌فرض
CPU_PERCENT         = 30             # ⚡ ۳۰٪ توان — همون که خواستی
XMRIG_PATH          = str(BASE_DIR / "xmrig.exe")
WALLETS_FILE        = DATA_DIR / "wallets.json"
MINING_STATE        = DATA_DIR / "mining_state.json"

def get_default_wallet(coin: str) -> str:
    return {
        "BTC": DEFAULT_WALLET_BTC,
        "XMR": DEFAULT_WALLET_XMR,
    }.get(coin.upper(), "")
