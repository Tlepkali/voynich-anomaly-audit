import json, urllib.request, urllib.parse, unicodedata, re, threading, time, os
TARGET=60000
def norm(t, lang):
    if lang=="ar":
        t=re.sub(r"[ً-ْـٰ]","",t)      # огласовки и татвиль
        t=re.sub(r"[^ء-ي]+"," ",t)
    elif lang=="sa":
        t=re.sub(r"[^ऀ-ॿ]+"," ",t)               # деванагари как есть, с матрами
    return re.sub(r"\s+"," ",t).strip()
def worker(lang):
    path=f"ref/wiki_{lang}.clean"
    have=open(path).read() if os.path.exists(path) else ""
    t0=time.time()
    while len(have)<TARGET and time.time()-t0<540:
        q=urllib.parse.urlencode({"action":"query","generator":"random","grnnamespace":"0",
            "grnlimit":"20","prop":"extracts","explaintext":"1","exlimit":"20",
            "format":"json","formatversion":"2"})
        try:
            req=urllib.request.Request(f"https://{lang}.wikipedia.org/w/api.php?{q}",
                                       headers={"User-Agent":"research/1.0"})
            d=json.load(urllib.request.urlopen(req, timeout=20))
        except Exception:
            time.sleep(0.4); continue
        c=norm(" ".join(p.get("extract","") for p in d.get("query",{}).get("pages",[])), lang)
        if c: have=(have+" "+c).strip(); open(path,"w").write(have)
ts=[threading.Thread(target=worker,args=(l,)) for l in ("ar","sa")]
for t in ts: t.start()
for t in ts: t.join()
