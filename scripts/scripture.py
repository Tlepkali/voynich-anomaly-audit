import json, urllib.request, re, unicodedata, os
def get(u, timeout=40):
    req=urllib.request.Request(u, headers={"User-Agent":"research/1.0"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8","replace")
# 1. Вульгата (латынь)
books=["genesis","exodus","leviticus","numbers","deuteronomy","joshua","judges","ruth",
       "samuel1","samuel2","kings1","kings2","psalms","proverbs","isaiah","jeremiah"]
out=[]
for b in books:
    try: out.append(get(f"http://www.thelatinlibrary.com/bible/{b}.shtml"))
    except Exception: pass
    if sum(len(x) for x in out)>900000: break
t=" ".join(out)
t=re.sub(r'(?is)<(script|style).*?</\1>'," ",t); t=re.sub(r'(?s)<[^>]+>'," ",t)
t=unicodedata.normalize("NFKD", t); t="".join(c for c in t if not unicodedata.combining(c))
t=re.sub(r"[^a-zA-Z]+"," ",t).lower()
open("ref/scr_vulgata.clean","w").write(re.sub(r"\s+"," ",t).strip())
# 2. Коран (арабский)
d=json.load(open("ref/quran.json"))
q=" ".join(v["text"] for ch in d.values() for v in ch)
q=re.sub(r"[ً-ْٰـۡ۟-ۭ]","",q)
q=re.sub(r"[^ء-ي]+"," ",q)
open("ref/scr_quran.clean","w").write(re.sub(r"\s+"," ",q).strip())
# 3. Танах (иврит, WLC)
bk=["Gen","Exod","Lev","Num","Deut","Josh","Judg","1Sam","2Sam","1Kgs","2Kgs","Isa","Jer","Ps","Prov"]
words=[]
for b in bk:
    try: x=get(f"https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/{b}.xml")
    except Exception: continue
    words += re.findall(r"<w[^>]*>([^<]+)</w>", x)
    if len(words)>200000: break
h=" ".join(words)
h=unicodedata.normalize("NFD", h); h="".join(c for c in h if not unicodedata.combining(c))
h=re.sub(r"[^א-ת]+"," ",h)
open("ref/scr_tanakh.clean","w").write(re.sub(r"\s+"," ",h).strip())
for n in ("vulgata","quran","tanakh"):
    c=open(f"ref/scr_{n}.clean").read(); ws=c.split()
    print(f"  {n:10s} {len(ws):>7,} слов, алфавит {len(set(c))-1:3d}, ср.длина {sum(len(w) for w in ws)/max(1,len(ws)):.2f}")
