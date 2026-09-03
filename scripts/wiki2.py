import json, urllib.request, urllib.parse, unicodedata, re, threading, time, os
TARGET=160000
def norm(t, lang):
    t=unicodedata.normalize("NFKD", t)
    if lang in ("it","de","en","la"):
        t="".join(c for c in t if not unicodedata.combining(c)).lower()
        t=re.sub(r"[^a-z]+"," ",t)
    elif lang=="el":
        t="".join(c for c in t if not unicodedata.combining(c)).lower()
        t=re.sub(r"[^Ͱ-Ͽ]+"," ",t)
    elif lang=="he":
        t="".join(c for c in t if not unicodedata.combining(c))
        t=re.sub(r"[^א-ת]+"," ",t)
    return re.sub(r"\s+"," ",t).strip()
def worker(lang):
    path=f"ref/wiki_{lang}.clean"
    have=open(path).read() if os.path.exists(path) else ""
    t0=time.time()
    while len(have)<TARGET and time.time()-t0<600:
        q=urllib.parse.urlencode({"action":"query","generator":"random","grnnamespace":"0",
            "grnlimit":"20","prop":"extracts","explaintext":"1","exlimit":"20",
            "format":"json","formatversion":"2"})
        try:
            req=urllib.request.Request(f"https://{lang}.wikipedia.org/w/api.php?{q}",
                                       headers={"User-Agent":"research/1.0"})
            d=json.load(urllib.request.urlopen(req, timeout=20))
        except Exception:
            time.sleep(0.5); continue
        chunk=" ".join(p.get("extract","") for p in d.get("query",{}).get("pages",[]))
        c=norm(chunk, lang)
        if c: have=(have+" "+c).strip(); open(path,"w").write(have)
    return
ts=[threading.Thread(target=worker,args=(l,)) for l in ("it","de","el","he","en","la")]
for t in ts: t.start()
for t in ts: t.join()
for l in ("it","de","el","he","en","la"):
    c=open(f"ref/wiki_{l}.clean").read(); ws=c.split()
    print(f"  {l}: {len(c):>8,} знаков, {len(ws):>7,} слов, алфавит {len(set(c))-1}, ср.длина {sum(len(w) for w in ws)/max(1,len(ws)):.2f}")
