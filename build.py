#!/usr/bin/env python3
"""Build index.html, The restaurant's page of the 2026 Reels that work for Barcelona restaurants, from ../research/scout.json."""
from __future__ import annotations

import html
import json
import statistics
from collections import defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCOUT = json.loads((HERE.parent / "research" / "scout.json").read_text())
TODAY = date(2026, 10, 27)

# Each format: its title, why it works, the Reels that show it, and what we film at El Tiet.
FORMATS = [
    ("👨‍🍳", "El xef explica la recepta d'un clàssic",
     "El cuiner, a càmera, ensenya com fa un plat de tota la vida. La gent el desa i el comenta.",
     ["Dbp-AbSsdaQ", "DaUc5IIsFOE"],
     "L'Iván explica en 30 segons com fa un plat seu: el suquet, un guisat, el que vulgui. En català, amb la seva gràcia."),
    ("🔥", "El foc i el producte, molt de prop",
     "Res més: la brasa, el plat que es fa, el so. Senzill i molt vist.",
     ["DaViLpXsvrO", "DeFE5Gkg2xd", "Db3HaHEhehL"],
     "La brasa, el bufador, la salsa que bull, molt a prop, amb el so real. El suquet d'avui ja és d'aquest tipus."),
    ("🍷", "Un plat i el seu vi",
     "Un plat, una copa, un nom de vi. Ajuda a decidir què demanar.",
     ["Db8mb5ZtFLc"],
     "Un plat de la carta i el vi que hi recomaneu, servit a taula."),
    ("✨", "Tot el restaurant en un vídeo",
     "15 segons de servei: sala plena, cuina, plats que surten. Fa venir ganes d'anar-hi.",
     ["DakiZU2Dk_b"],
     "Un vespre de servei: la sala, la cuina, els plats sortint, l'equip rient. Clips curts, molts."),
    ("📺", "Una sèrie per capítols",
     "«Capítol 1», «Capítol 2»... La gent torna per veure el següent.",
     ["Dbs_kTpkfXJ"],
     "«El producte de la setmana»: cada setmana un producte que compra l'Iván, del mercat al plat."),
    ("📱", "Un creador de menjar us visita",
     "El que fa més visualitzacions de tot: un creador que dina al restaurant. Aquest és a Mallorca 250, a cinc minuts d'El Tiet.",
     ["De6aBA4ukSm"],
     "Convidar a dinar un creador de menjar de Barcelona. Us busquem els que encaixen."),
]


def median_views() -> dict[str, float]:
    per = defaultdict(list)
    for x in SCOUT.values():
        if x.get("kind") == "clips" and x.get("views"):
            per[x["user"]].append(x["views"])
    return {u: statistics.median(v) for u, v in per.items() if len(v) >= 5}


def ago(day: str) -> str:
    n = (TODAY - date.fromisoformat(day)).days
    if n < 14:
        return f"fa {n} dies"
    if n < 60:
        return f"fa {n // 7} setmanes"
    return f"fa {round(n / 30.4)} mesos"


def num(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def card(code: str, med: dict) -> str:
    x = SCOUT[code]
    url = f"https://www.instagram.com/reel/{code}/"
    times = x["views"] / med[x["user"]] if x["user"] in med else None
    boost = f'<div class="boost">{round(times)} vegades més vist que els seus vídeos normals</div>' if times and times >= 2 else ""
    return f'''<div class="reel">
<div class="who"><b>{html.escape(x["user_name"])}</b> · {ago(x["taken_at"])}</div>
<div class="nums">👁 {num(x["views"])} &nbsp; ❤️ {num(x["likes"])} &nbsp; 💬 {num(x["comments"])}</div>
{boost}
<button class="slot" data-embed="{url}embed/" aria-label="Mira el vídeo"><img src="img/{code}.jpg" alt="" loading="lazy"><span class="play">▶</span></button>
<a class="open" href="{url}">Obrir a Instagram ↗</a>
</div>'''


def main() -> None:
    med = median_views()
    blocks = []
    for i, (icon, title, why, codes, ask) in enumerate(FORMATS, 1):
        reels = "\n".join(card(c, med) for c in codes)
        blocks.append(f'''<section class="fmt">
<h2><span class="n">{i}</span> {icon} {html.escape(title)}</h2>
<p class="why">{html.escape(why)}</p>
{reels}
<div class="ask"><b>A El Tiet:</b> {html.escape(ask)}</div>
</section>''')
    page = (HERE / "template.html").read_text().replace("{{FORMATS}}", "\n".join(blocks))
    (HERE / "index.html").write_text(page)
    print("index.html", len(page))


if __name__ == "__main__":
    main()
