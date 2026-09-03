import json, urllib.request, urllib.parse, re, threading, time, os, random
TARGET=45000
SEEDS={"mn":["түүх","шинжлэх","хот","хөгжим","ургамал","математик","дайн","соёл","анагаах","одон",
             "гүн","улс","амьтан","уран","төмөр","газар"],
       "ka":["ისტორია","მეცნიერება","ქალაქი","მუსიკა","მცენარე","მათემატიკა","ომი","კულტურა",
             "მედიცინა","ასტრონომია","ფილოსოფია","სახელმწიფო","ცხოველი","ლიტერატურა","რკინიგზა","ენა"]}
def norm(t, lang):
    if lang=="mn":
        t=t.lower(); t=re.sub(r"[^а-яёөү]+"," ",t)
    else:
        t=re.sub(r"[^ა-ჿ]+"," ",t)
    return re.sub(r"\s+"," ",t).strip()
def worker(lang):
    path=f"ref/wiki_{lang}.clean"
    have=open(path).read() if os.path.exists(path) else ""
    rnd=random.Random(11); t0=time.time(); seen=set()
    while len(have)<TARGET and time.time()-t0<480:
        term=rnd.choice(SEEDS[lang])
        q=urllib.parse.urlencode({"action":"query","generator":"search",
            "gsrsearch":term,"gsrlimit":"20","gsroffset":str(rnd.randrange(0,120)),
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
ts=[threading.Thread(target=worker,args=(l,)) for l in ("mn","ka")]
for t in ts: t.start()
for t in ts: t.join()
