# -*- coding: utf-8 -*-
"""Добор одного языка с ЗАПИСЬЮ ПО ХОДУ — прогресс не теряется при остановке."""
import json, urllib.request, urllib.parse, unicodedata, re, sys, time, os
def norm(t):
    t=unicodedata.normalize("NFKD", t)
    t="".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+"," ","".join(c if unicodedata.category(c).startswith("L") else " " for c in t)).strip()
lang=sys.argv[1]; target=int(sys.argv[2]); path=f"ref/wiki_{lang}.clean"
buf=[open(path,encoding="utf-8",errors="ignore").read()] if os.path.exists(path) else []
words=len(buf[0].split()) if buf else 0
print(f"старт: {words} слов, цель {target}", flush=True)
tries=0
while words<target and tries<1200:
    tries+=1
    q=urllib.parse.urlencode({"action":"query","generator":"random","grnnamespace":"0",
        "grnlimit":"25","prop":"extracts","explaintext":"1","format":"json","formatversion":"2"})
    try:
        r=urllib.request.Request(f"https://{lang}.wikipedia.org/w/api.php?{q}",
                                 headers={"User-Agent":"voynich-corpus-research/1.0"})
        d=json.load(urllib.request.urlopen(r, timeout=30))
    except Exception:
        time.sleep(1.5); continue
    for p in d.get("query",{}).get("pages",[]):
        t=norm(p.get("extract",""))
        if len(t.split())>60: buf.append(t); words+=len(t.split())
    if tries%20==0:                                  # ЗАПИСЬ ПО ХОДУ
        open(path,"w",encoding="utf-8").write(" ".join(buf))
        print(f"  {words} слов, попыток {tries}", flush=True)
    time.sleep(0.12)
open(path,"w",encoding="utf-8").write(" ".join(buf))
print(f"ГОТОВО: {words} слов за {tries} попыток → {path}", flush=True)
