import json, urllib.request, urllib.parse, re, threading, time, os, random
TARGET=40000
SEEDS={"zh":["歷史","科學","城市","音樂","植物","數學","戰爭","文化","醫學","天文",
             "language","哲學","建築","國家","動物","文學"],
       "ja":["歴史","科学","都市","音楽","植物","数学","戦争","文化","医学","天文",
             "哲学","建築","国家","動物","文学","鉄道"]}
def norm(t, lang):
    t=re.sub(r"[^぀-ヿ一-鿿㐀-䶿]+"," ",t)  # кана и иероглифы
    return re.sub(r"\s+"," ",t).strip()
def worker(lang):
    path=f"ref/wiki_{lang}.clean"
    have=open(path).read() if os.path.exists(path) else ""
    rnd=random.Random(7); t0=time.time(); seen=set()
    while len(have)<TARGET and time.time()-t0<500:
        term=rnd.choice(SEEDS[lang])
        q=urllib.parse.urlencode({"action":"query","generator":"search",
            "gsrsearch":term,"gsrlimit":"20","gsroffset":str(rnd.randrange(0,150)),
            "prop":"extracts","explaintext":"1","exlimit":"20",
            "format":"json","formatversion":"2"})
        try:
            req=urllib.request.Request(f"https://{lang}.wikipedia.org/w/api.php?{q}",
                                       headers={"User-Agent":"research/1.0"})
            d=json.load(urllib.request.urlopen(req, timeout=20))
        except Exception:
            time.sleep(0.3); continue
        parts=[]
        for p in d.get("query",{}).get("pages",[]):
            if p.get("pageid") in seen: continue
            seen.add(p.get("pageid")); parts.append(p.get("extract",""))
        c=norm(" ".join(parts), lang)
        if c: have=(have+c).strip(); open(path,"w").write(have)
ts=[threading.Thread(target=worker,args=(l,)) for l in ("zh","ja")]
for t in ts: t.start()
for t in ts: t.join()
