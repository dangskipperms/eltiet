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
     ["DaUc5IIsFOE", "DZX6NT8oikL", "DdtWJnzM259"],
     "L'Iván explica en 30 segons com fa un plat seu: el suquet, un guisat, el que vulgui. En català, amb la seva gràcia."),
    ("🔥", "El plat i el foc, molt de prop",
     "Res més: la brasa, el plat que es fa, el so. Senzill.",
     ["Dc1F3cmFNdw", "Db3HaHEhehL", "DeuYpYvxGp9"],
     "La brasa, el bufador, la salsa que bull, molt a prop, amb el so real. El suquet d'avui ja és d'aquest tipus."),
    ("📺", "Una sèrie per capítols",
     "«Capítol 1», «Capítol 2»... La gent torna per veure el següent.",
     ["Dbs_kTpkfXJ"],
     "«El producte de la setmana»: cada setmana un producte que compra l'Iván, del mercat al plat."),
    ("👥", "L'equip, a la cuina per dins",
     "Les persones que hi ha darrere dels plats. Fa proper el restaurant.",
     ["Dak5aiUEyxe", "DYzmcWZjxBB"],
     "Un matí a la cuina d'El Tiet: l'Iván, la Bea, la preparació. Clips curts, sense posar."),
    ("🥂", "Els clients de sempre",
     "Un client de tota la vida explica per què torna. Genera confiança.",
     ["Daa5Y5FtCaH", "DbtL_rys3st"],
     "Un client fidel, 20 segons a càmera: què demana sempre i per què."),
    ("📱", "Un creador de menjar us visita",
     "El que fa més m'agrada de tot: un creador que dina al restaurant. Aquest és a Mallorca 250, a cinc minuts d'El Tiet.",
     ["De6aBA4ukSm"],
     "Convidar a dinar un creador de menjar de Barcelona. Us busquem els que encaixen."),
]

def median_likes() -> dict[str, float]:
    # Likes, not views: views can be bought with ads, likes come from people who liked it.
    per = defaultdict(list)
    for x in SCOUT.values():
        if x.get("kind") == "clips" and x.get("likes") is not None:
            per[x["user"]].append(x["likes"])
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
    times = x["likes"] / med[x["user"]] if med.get(x["user"]) else None
    boost = f'<div class="boost">{round(times)} vegades més m\'agrada que els seus vídeos normals</div>' if times and times >= 2 else ""
    return f'''<div class="reel">
<div class="who"><b>{html.escape(x["user_name"])}</b> · {ago(x["taken_at"])}</div>
<div class="nums">❤️ {num(x["likes"])} &nbsp; 💬 {num(x["comments"])} &nbsp; <span class="views">👁 {num(x["views"])}</span></div>
{boost}
<button class="slot" data-embed="{url}embed/" aria-label="Mira el vídeo"><img src="img/{code}.jpg" alt="" loading="lazy"><span class="play">▶</span></button>
<a class="open" href="{url}">Obrir a Instagram ↗</a>
</div>'''


def main() -> None:
    med = median_likes()
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
