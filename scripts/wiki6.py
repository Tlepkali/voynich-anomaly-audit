import json, urllib.request, urllib.parse, re, threading, time, os, random, unicodedata
TARGET=45000
SEEDS={"tr":["tarih","bilim","şehir","müzik","bitki","matematik","savaş","kültür","tıp","gökbilim",
             "felsefe","mimarlık","devlet","hayvan","edebiyat","demiryolu"],
       "ko":["역사","과학","도시","음악","식물","수학","전쟁","문화","의학","천문",
             "철학","건축","국가","동물","문학","철도"]}
def norm(t, lang):
    if lang=="tr":
        t=t.lower(); t=re.sub(r"[^a-zçğıöşü]+"," ",t)
    else:
        t=unicodedata.normalize("NFD", t)          # хангыль -> чамо
        t=re.sub(r"[^ᄀ-ᇿ]+"," ",t)
    return re.sub(r"\s+"," ",t).strip()
def worker(lang):
    path=f"ref/wiki_{lang}.clean"
    have=open(path).read() if os.path.exists(path) else ""
    rnd=random.Random(3); t0=time.time(); seen=set()
    while len(have)<TARGET and time.time()-t0<480:
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
        if c: have=(have+" "+c).strip(); open(path,"w").write(have)
ts=[threading.Thread(target=worker,args=(l,)) for l in ("tr","ko")]
for t in ts: t.start()
for t in ts: t.join()
