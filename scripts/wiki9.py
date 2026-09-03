import json, urllib.request, urllib.parse, re, threading, time, os, random, unicodedata
TARGET=42000
SEEDS={"eu":["historia","zientzia","hiria","musika","landare","matematika","gerra","kultura",
             "medikuntza","astronomia","filosofia","estatua","animalia","literatura","trenbidea","hizkuntza"],
       "fi":["historia","tiede","kaupunki","musiikki","kasvi","matematiikka","sota","kulttuuri",
             "lääketiede","tähtitiede","filosofia","valtio","eläin","kirjallisuus","rautatie","kieli"]}
def norm(t):
    t=unicodedata.normalize("NFKD", t).lower()
    t="".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+"," ", re.sub(r"[^a-z]+"," ", t)).strip()
def worker(lang):
    path=f"ref/wiki_{lang}.clean"
    have=open(path).read() if os.path.exists(path) else ""
    rnd=random.Random(23); t0=time.time(); seen=set()
    while len(have)<TARGET and time.time()-t0<420:
        term=rnd.choice(SEEDS[lang])
        q=urllib.parse.urlencode({"action":"query","generator":"search","gsrsearch":term,
            "gsrlimit":"20","gsroffset":str(rnd.randrange(0,120)),"prop":"extracts",
            "explaintext":"1","exlimit":"20","format":"json","formatversion":"2"})
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
        c=norm(" ".join(parts))
        if c: have=(have+" "+c).strip(); open(path,"w").write(have)
ts=[threading.Thread(target=worker,args=(l,)) for l in ("eu","fi")]
for t in ts: t.start()
for t in ts: t.join()
