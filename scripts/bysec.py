import json, random, sys, collections
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
SEC={"T":"только текст","H":"травник","A":"астроном.","Z":"зодиак",
     "B":"«банный»","C":"космолог.","P":"аптечный","S":"звёзды/рецепты"}
LINES=[]
for r in [r for r in rows if r["locus"]=="P"]:
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=3:
        m=pages.get(r["page"],{})
        LINES.append({"w":ws,"L":m.get("L","?"),"I":m.get("I","?"),"H":m.get("H","?")})

def lcp(a,b):
    ga,gb=metrics.merge(a),metrics.merge(b); n=0
    for x,y in zip(ga,gb):
        if x!=y: break
        n+=1
    return n
def deltas(lines):
    out=[]
    for l in lines:
        w=l["w"]; n=len(w); v=[]
        for i in range(n-2): v.append(lcp(w[i],w[i+2])-lcp(w[i],w[i+1]))
        if v: out.append(sum(v)/len(v))
    return out
def shuf(lines, seed=5):
    rnd=random.Random(seed); o=[]
    for l in lines:
        w=l["w"][:]; rnd.shuffle(w); o.append({"w":w})
    return o
def boot(v, n=4000, seed=13):
    if len(v)<40: return None
    rnd=random.Random(seed); N=len(v); r=[]
    for _ in range(n): r.append(sum(v[rnd.randrange(N)] for _ in range(N))/N)
    r.sort(); return sum(v)/N, r[int(.025*n)], r[int(.975*n)]
def report(label, lines, indent="  "):
    d=deltas(lines); b=boot(d)
    if not b: print(f"{indent}{label:30s} строк {len(d):5d}   мало данных"); return
    m,lo,hi=b
    c=boot(deltas(shuf(lines)), seed=29)
    mark = "ВЫШЕ ✓" if lo>0 else ("ниже ✗" if hi<0 else "неотличимо ·")
    print(f"{indent}{label:30s} строк {len(d):5d}   {m:+.4f} [{lo:+.4f}, {hi:+.4f}]  {mark:12s}"
          f" контроль {c[0]:+.4f}")

B=[l for l in LINES if l["L"]=="B"]
print("="*92); print("ЭФФЕКТ d=2 В КАРРИЕРЕ B — ПО РАЗДЕЛАМ (разделы и руки переплетены!)"); print("="*92)
report("ВЕСЬ Карриер B", B)
print()
for s,_ in collections.Counter(l["I"] for l in B).most_common():
    ls=[l for l in B if l["I"]==s]
    if len(ls)>=55: report(SEC.get(s,s), ls)

print("\n"+"="*92); print("ТО ЖЕ ПО РУКАМ"); print("="*92)
for h,_ in collections.Counter(l["H"] for l in B).most_common():
    ls=[l for l in B if l["H"]==h]
    if len(ls)>=55: report(f"рука {h}", ls)

print("\n"+"="*92)
print("ЧИСТЫЙ СРЕЗ 1: разделы ВНУТРИ одной руки — влияет ли содержание?")
print("="*92)
for h in ("2","3"):
    hs=[l for l in B if l["H"]==h]
    if len(hs)<200: continue
    print(f"  рука {h}:")
    for s,_ in collections.Counter(l["I"] for l in hs).most_common():
        ls=[l for l in hs if l["I"]==s]
        if len(ls)>=55: report(SEC.get(s,s), ls, indent="     ")

print("\n"+"="*92)
print("ЧИСТЫЙ СРЕЗ 2: руки ВНУТРИ одного раздела (травник) — влияет ли писец?")
print("="*92)
herb=[l for l in B if l["I"]=="H"]
for h,_ in collections.Counter(l["H"] for l in herb).most_common():
    ls=[l for l in herb if l["H"]==h]
    if len(ls)>=55: report(f"травник, рука {h}", ls)
