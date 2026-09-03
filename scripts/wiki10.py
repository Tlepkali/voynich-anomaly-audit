import json, urllib.request, urllib.parse, re, threading, time, os, random, unicodedata
TARGET=45000
SEEDS={"cu":["богъ","землꙗ","чловѣкъ","градъ","книга","црькꙑ","вода","слово"],
       "is":["saga","vísindi","borg","tónlist","planta","stærðfræði","stríð","menning","læknisfræði","stjörnufræði"],
       "cs":["historie","věda","město","hudba","rostlina","matematika","válka","kultura","medicína","astronomie"],
       "pl":["historia","nauka","miasto","muzyka","roślina","matematyka","wojna","kultura","medycyna","astronomia"],
       "sv":["historia","vetenskap","stad","musik","växt","matematik","krig","kultur","medicin","astronomi"],
       "da":["historie","videnskab","by","musik","plante","matematik","krig","kultur","medicin","astronomi"],
       "ru":["история","наука","город","музыка","растение","математика","война","культура","медицина","астрономия"]}
CYR=set("абвгдежзийклмнопрстуфхцчшщъыьэюяѣѫѧѩѭꙋѹѡѳѵꙗ")
def norm(t, lang):
    t=unicodedata.normalize("NFKD", t)
    t="".join(c for c in t if not unicodedata.combining(c))
    t=t.lower()
    if lang in ("cu","ru"):
        t=re.sub(r"[^"+"".join(CYR)+r"]+"," ",t)
    else:
        t=re.sub(r"[^a-zàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]+"," ",t)
    return re.sub(r"\s+"," ",t).strip()
def worker(lang):
    path=f"ref/wiki_{lang}.clean"
    have=open(path).read() if os.path.exists(path) else ""
    rnd=random.Random(5); t0=time.time(); seen=set()
    while len(have)<TARGET and time.time()-t0<420:
        term=rnd.choice(SEEDS[lang])
        q=urllib.parse.urlencode({"action":"query","generator":"search","gsrsearch":term,
            "gsrlimit":"20","gsroffset":str(rnd.randrange(0,100)),"prop":"extracts",
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
        c=norm(" ".join(parts), lang)
        if c: have=(have+" "+c).strip(); open(path,"w").write(have)
ts=[threading.Thread(target=worker,args=(l,)) for l in ("cu","is","cs","pl","sv","da","ru")]
for t in ts: t.start()
for t in ts: t.join()
