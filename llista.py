#!/usr/bin/env python3
"""A list of Reels for her phone: tap one, it fills the screen, swipe or «Següent» for the next. Instagram is one small link.
python3 llista.py <slug> reads llista/<slug>/list.json and writes llista/<slug>/index.html.
list.json: {"title", "intro", "items": [{"code", "line", "x"?}]}, best first. "x" is the multiplier label, left out when none.
Each Reel's video comes from ../research/raw-reels/ (instagram/scout.py fetch), shrunk once into vid/, its cover into img/.
The page lives at https://dangskipperms.github.io/eltiet/llista/<slug>/ once pushed.
Its drawing, kept for conformity: ../docs/drawings/llista-videos/."""
import html, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE.parent / "research" / "raw-reels"
SCOUT = json.loads((HERE.parent / "research" / "scout.json").read_text())


def numbers(code):
    """Views, likes, comments and the day posted, as the search saved them. Under ten likes is a hidden count: left out."""
    s = SCOUT.get(code, {})
    likes = s.get("likes")
    return {"views": s.get("views"), "likes": likes if likes is not None and likes >= 10 else None,
            "comments": s.get("comments"), "date": s.get("taken_at")}


def media(code):
    """540 wide fills a phone sharp enough, ~3 MB a minute. A file already there is kept."""
    v, c = HERE / "vid" / f"{code}.mp4", HERE / "img" / f"{code}.jpg"
    if not v.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(RAW / f"{code}.mp4"), "-vf", "scale=540:-2", "-c:v", "libx264",
                        "-crf", "30", "-preset", "medium", "-c:a", "aac", "-b:a", "64k", "-ac", "1", "-movflags", "+faststart", str(v)],
                       check=True)
    if not c.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", str(v), "-frames:v", "1", "-vf", "scale=360:-2", "-q:v", "4", str(c)],
                       check=True)


def main(slug):
    d = HERE / "llista" / slug
    L = json.loads((d / "list.json").read_text())
    items = [{"code": i["code"], "line": i["line"], "x": i.get("x", ""), "url": f"https://www.instagram.com/reel/{i['code']}/", **numbers(i["code"])}
             for i in L["items"]]
    for i in items:
        media(i["code"])
    page = (HERE / "llista.template.html").read_text()
    for k, v in {"TITLE": html.escape(L["title"]), "INTRO": html.escape(L["intro"]), "SLUG": slug,
                 "HOW_HIDDEN": "" if any(i["x"] for i in items) else "hidden",
                 "DATA": json.dumps(items, ensure_ascii=False).replace("</", "<\\/")}.items():
        page = page.replace("{{" + k + "}}", v)
    assert "{{" not in page
    (d / "index.html").write_text(page)
    mb = sum((HERE / "vid" / f"{i['code']}.mp4").stat().st_size for i in items) / 1e6
    print(f"llista/{slug}/index.html · {len(items)} Reels · {mb:.0f} MB of video")


if __name__ == "__main__":
    main(sys.argv[1])
