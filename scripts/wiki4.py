import json, urllib.request, urllib.parse, re, threading, time, os, random
TARGET=40000
SEEDS={"ar":["مصر","الإسلام","التاريخ","اللغة","العلم","الحرب","المدينة","الدولة","النبات","الطب",
             "الفلك","الرياضيات","الموسيقى","الفلسفة","البحر","الجبل","الملك","الكتاب"],
       "sa":["भारतम्","संस्कृतम्","वेदः","देवः","राजा","नगरम्","जलम्","पर्वतः","शास्त्रम्","काव्यम्",
             "गणितम्","इतिहासः","धर्मः","विद्या","वृक्षः","सूर्यः"]}
def norm(t, lang):
    if lang=="ar":
        t=re.sub(r"[ً-ْـٰ]","",t)
        t=re.sub(r"[^ء-ي]+"," ",t)
    else:
        t=re.sub(r"[^ऀ-ॿ]+"," ",t)
    return re.sub(r"\s+"," ",t).strip()
def worker(lang):
    path=f"ref/wiki_{lang}.clean"
    have=open(path).read() if os.path.exists(path) else ""
    rnd=random.Random(1); t0=time.time(); seen=set()
    while len(have)<TARGET and time.time()-t0<900:
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
    print(f"{lang}: {len(have)} знаков")
ts=[threading.Thread(target=worker,args=(l,)) for l in ("ar","sa")]
for t in ts: t.start()
for t in ts: t.join()
