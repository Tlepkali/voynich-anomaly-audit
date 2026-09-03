# -*- coding: utf-8 -*-
"""Добор корпусов до объёма рукописи и выше. Нормализация одна для всех:
оставляем только буквы (категория L), снимаем комбинирующие знаки, приводим к нижнему регистру."""
import json, urllib.request, urllib.parse, unicodedata, re, sys, time, os
def norm(t):
    t=unicodedata.normalize("NFKD", t)
    t="".join(c for c in t if not unicodedata.combining(c))
    t=t.lower()
    out=[]
    for c in t:
        out.append(c if unicodedata.category(c).startswith("L") else " ")
    return re.sub(r"\s+"," ","".join(out)).strip()
def fetch(lang, need_words, path, log):
    have=""
    if os.path.exists(path): have=open(path,encoding="utf-8",errors="ignore").read()
    words=len(have.split()); tries=0; buf=[have] if have else []
    while words<need_words and tries<600:
        tries+=1
        q=urllib.parse.urlencode({"action":"query","generator":"random","grnnamespace":"0",
            "grnlimit":"25","prop":"extracts","explaintext":"1","format":"json","formatversion":"2"})
        try:
            req=urllib.request.Request(f"https://{lang}.wikipedia.org/w/api.php?{q}",
                                       headers={"User-Agent":"voynich-corpus-research/1.0"})
            d=json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            time.sleep(1.5); continue
        got=0
        for p in d.get("query",{}).get("pages",[]):
            t=norm(p.get("extract",""))
            if len(t.split())>60: buf.append(t); got+=len(t.split())
        words+=got
        if tries%25==0: print(f"    {lang}: {words} слов, попыток {tries}", flush=True)
        time.sleep(0.15)
    open(path,"w",encoding="utf-8").write(" ".join(buf))
    print(f"  {lang:>4s} → {words:7d} слов  ({path})", flush=True)
    return words
TARGET=220000
LANGS=sys.argv[1:] or ["mn","he","sa","fi","tr","eu","cs","ru","pl","is","da","sv","el","it","de","ar","la","en"]
for lg in LANGS:
    p=f"ref/wiki_{lg}.clean"
    n=len(open(p,encoding='utf-8',errors='ignore').read().split()) if os.path.exists(p) else 0
    if n>=TARGET:
        print(f"  {lg:>4s} уже {n} слов — пропуск", flush=True); continue
    fetch(lg, TARGET, p, None)
print("ГОТОВО", flush=True)
