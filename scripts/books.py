# -*- coding: utf-8 -*-
"""Книжные корпуса: одна работа одного автора — жанрово ближе к рукописи, чем скрейп Википедии."""
import urllib.request, unicodedata, re, os, sys
BOOKS={   # id проекта Гутенберг -> (имя, язык)
 "2000":"es_quijote", "17489":"de_faust", "1012":"it_inferno", "14158":"fr_candide",
 "10662":"la_confessiones", "2554":"ru_crime", "27827":"grc_iliad", "23428":"pt_lusiadas",
 "1184":"fr_montecristo", "6130":"grc_iliad2", "3300":"en_wealth", "2148":"en_poe",
}
def norm(t):
    t=unicodedata.normalize("NFKD",t)
    t="".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+"," ","".join(c if unicodedata.category(c).startswith("L") else " " for c in t)).strip()
def strip_gutenberg(t):
    a=re.search(r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", t, re.S)
    b=re.search(r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG", t, re.S)
    if a: t=t[a.end():]
    if b: t=t[:b.start()]
    return t
for gid,name in BOOKS.items():
    p=f"ref/bk_{name}.clean"
    if os.path.exists(p) and len(open(p,encoding='utf-8',errors='ignore').read().split())>30000:
        print(f"  {name}: уже есть"); continue
    ok=False
    for u in (f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt",
              f"https://www.gutenberg.org/files/{gid}/{gid}-0.txt"):
        try:
            r=urllib.request.Request(u, headers={"User-Agent":"voynich-corpus-research/1.0"})
            raw=urllib.request.urlopen(r, timeout=45).read().decode("utf-8", errors="replace")
            w=norm(strip_gutenberg(raw))
            if len(w.split())>20000:
                open(p,"w",encoding="utf-8").write(w)
                print(f"  {name:>16s}: {len(w.split()):7d} слов"); ok=True; break
        except Exception as e:
            continue
    if not ok: print(f"  {name:>16s}: НЕ ВЫШЛО")
