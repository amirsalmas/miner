COINS = {
    "BTC": {
        "name": "Bitcoin", "symbol": "BTC", "icon": "₿",
        "cpu_ok": False,
        "address_regex": r"^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}$",
        "pools": [
            {"name": "Solo ckpool (شانس ۱ در میلیون)", "url": "solo.ckpool.org:3333"},
            {"name": "Braiins Solo", "url": "stratum.braiins.com:3333"},
        ],
        "note": "ماین بیت‌کوین با CPU از نظر اقتصادی صفر است. فقط برای تست/آزمایش.",
    },
    "XMR": {
        "name": "Monero", "symbol": "XMR", "icon": "🔶",
        "cpu_ok": True,
        "address_regex": r"^(4|8)[1-9A-HJ-NP-Za-km-z]{94}$",
        "pools": [
            {"name": "SupportXMR", "url": "pool.supportxmr.com:3333"},
            {"name": "MoneroOcean", "url": "gulf.moneroocean.stream:10001"},
            {"name": "HashVault", "url": "pool.hashvault.pro:3333"},
        ],
    },
    "WOW": {
        "name": "Wownero", "symbol": "WOW", "icon": "🐶",
        "cpu_ok": True,
        "address_regex": r"^Wo[1-9A-HJ-NP-Za-km-z]{95}$",
        "pools": [{"name": "wownero.lol", "url": "pool.wownero.lol:3333"}],
    },
}

def list_coins():
    return [{
        "code": c, "name": v["name"], "symbol": v["symbol"],
        "icon": v["icon"], "cpu_ok": v["cpu_ok"],
        "pools": v["pools"], "note": v.get("note", ""),
    } for c, v in COINS.items()]

def get_coin(code):
    return COINS.get(code.upper())
