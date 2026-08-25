#!/usr/bin/env python3
"""
Genera la lectura del horóscopo del día para los 12 signos y la guarda en
data/today.json. Pensado para correr una vez al día desde un GitHub Action
(ver .github/workflows/daily-horoscope.yml).

No usa ninguna API externa ni clave: elige de forma determinista (hash de
fecha + signo + categoría) entre un banco de contenido curado en
data/content_bank.json, así que el resultado es reproducible y gratuito,
y cambia automáticamente cada día.
"""
import hashlib
import json
import os
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Mexico_City")
except Exception:
    TZ = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK_PATH = os.path.join(ROOT, "data", "content_bank.json")
OUT_PATH = os.path.join(ROOT, "data", "today.json")

SIGNS = [
    {"id": "aries",       "name": "Aries",       "glyph": "♈", "dates": "21 mar – 19 abr"},
    {"id": "tauro",       "name": "Tauro",       "glyph": "♉", "dates": "20 abr – 20 may"},
    {"id": "geminis",     "name": "Géminis",     "glyph": "♊", "dates": "21 may – 20 jun"},
    {"id": "cancer",      "name": "Cáncer",      "glyph": "♋", "dates": "21 jun – 22 jul"},
    {"id": "leo",         "name": "Leo",         "glyph": "♌", "dates": "23 jul – 22 ago"},
    {"id": "virgo",       "name": "Virgo",       "glyph": "♍", "dates": "23 ago – 22 sep"},
    {"id": "libra",       "name": "Libra",       "glyph": "♎", "dates": "23 sep – 22 oct"},
    {"id": "escorpio",    "name": "Escorpio",    "glyph": "♏", "dates": "23 oct – 21 nov"},
    {"id": "sagitario",   "name": "Sagitario",   "glyph": "♐", "dates": "22 nov – 21 dic"},
    {"id": "capricornio", "name": "Capricornio", "glyph": "♑", "dates": "22 dic – 19 ene"},
    {"id": "acuario",     "name": "Acuario",     "glyph": "♒", "dates": "20 ene – 18 feb"},
    {"id": "piscis",      "name": "Piscis",      "glyph": "♓", "dates": "19 feb – 20 mar"},
]

MESES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto",
         "septiembre","octubre","noviembre","diciembre"]
DIAS = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]


def seeded_index(*parts, mod):
    h = hashlib.sha256("-".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(h, 16) % mod


def pick(pool, *seed_parts):
    return pool[seeded_index(*seed_parts, mod=len(pool))]


def main():
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        bank = json.load(f)

    now = datetime.now(TZ) if TZ else datetime.utcnow()
    date_iso = now.strftime("%Y-%m-%d")
    date_label = f"{DIAS[now.weekday()].capitalize()}, {now.day} de {MESES[now.month-1]} de {now.year}"

    readings = {}
    for sign in SIGNS:
        sid = sign["id"]
        compatible = SIGNS[seeded_index(date_iso, sid, "compat", mod=len(SIGNS))]
        if compatible["id"] == sid:
            compatible = SIGNS[(SIGNS.index(sign) + 4) % len(SIGNS)]
        readings[sid] = {
            "quote": pick(bank["quotes"], date_iso, sid, "quote"),
            "amor": pick(bank["amor"], date_iso, sid, "amor"),
            "trabajo": pick(bank["trabajo"], date_iso, sid, "trabajo"),
            "salud": pick(bank["salud"], date_iso, sid, "salud"),
            "numero": 1 + seeded_index(date_iso, sid, "numero", mod=99),
            "color": pick(bank["colors"], date_iso, sid, "color"),
            "compatible": {"id": compatible["id"], "name": compatible["name"], "glyph": compatible["glyph"]},
        }

    out = {
        "date_iso": date_iso,
        "date_label": date_label,
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "signs": SIGNS,
        "readings": readings,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Generado {OUT_PATH} para {date_label}")


if __name__ == "__main__":
    main()
