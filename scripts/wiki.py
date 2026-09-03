import json, urllib.request, urllib.parse, unicodedata, re, sys, time
def fetch(lang, need_chars=260000):
    out=[]; total=0; tries=0
    while total<need_chars and tries<45:
        tries+=1
        q=urllib.parse.urlencode({"action":"query","generator":"random","grnnamespace":"0",
            "grnlimit":"20","prop":"extracts","explaintext":"1","format":"json","formatversion":"2"})
        url=f"https://{lang}.wikipedia.org/w/api.php?{q}"
        try:
            req=urllib.request.Request(url, headers={"User-Agent":"research-script/1.0"})
            d=json.load(urllib.request.urlopen(req, timeout=25))
        except Exception as e:
            time.sleep(1); continue
        for p in d.get("query",{}).get("pages",[]):
            t=p.get("extract","")
            if len(t)>400: out.append(t); total+=len(t)
    return "\n".join(out)
RANGES={"it":"a-zà-ÿ","de":"a-zà-ÿ","el":"Ͱ-Ͽἀ-῿","he":"֐-׿",
        "en":"a-z","la":"a-z"}
def norm(t, lang):
    t=unicodedata.normalize("NFKD", t)
    if lang in ("it","de","en","la"):
        t="".join(c for c in t if not unicodedata.combining(c)).lower()
        t=re.sub(r"[^a-z]+"," ",t)
    elif lang=="el":
        t="".join(c for c in t if not unicodedata.combining(c)).lower()
        t=re.sub(r"[^Ͱ-Ͽ]+"," ",t)
    elif lang=="he":
        t="".join(c for c in t if not unicodedata.combining(c))   # снимаем огласовки
        t=re.sub(r"[^א-ת]+"," ",t)                       # только согласные буквы
    return re.sub(r"\s+"," ",t).strip()
for lang in sys.argv[1:]:
    raw=fetch(lang)
    cl=norm(raw, lang)
    open(f"ref/wiki_{lang}.clean","w").write(cl)
    ws=cl.split()
    print(f"  {lang}: {len(cl):>8,} знаков, {len(ws):>7,} слов, алфавит {len(set(cl))-1}, "
          f"ср.длина {sum(len(w) for w in ws)/max(1,len(ws)):.2f}")
