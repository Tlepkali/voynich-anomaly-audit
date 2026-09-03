import json, collections
D = json.load(open("parsed.json")); rows, pages = D["rows"], D["pages"]
voy = [w for r in rows for w in r["words"] if '?' not in w]
lat = open("ref/latin.clean").read().split()[:len(voy)]
eng = open("ref/english.clean").read().split()[:len(voy)]
def dist(ws, mx=13):
    c = collections.Counter(min(len(w),mx) for w in ws); T=len(ws)
    return [round(100*c.get(i,0)/T,2) for i in range(1,mx+1)]
out = {"lens": {"voy": dist(voy), "lat": dist(lat), "eng": dist(eng)}}
# разделы по $I
sec = collections.Counter()
for r in rows:
    i = pages.get(r["page"],{}).get("I","?")
    sec[i] += len([w for w in r["words"] if '?' not in w])
out["sections"] = dict(sec)
# страницы по языку Карриера
lang = collections.Counter(m.get("L","?") for m in pages.values())
out["langpages"] = dict(lang)
hands = collections.Counter(m.get("H","?") for m in pages.values())
out["hands"] = dict(hands)
print(json.dumps(out, ensure_ascii=False, indent=1))
