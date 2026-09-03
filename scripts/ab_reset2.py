import json, collections, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows, pages = D["rows"], D["pages"]
P=[r for r in rows if r["locus"]=="P"]
LINES=[]
for r in P:
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=3:
        LINES.append({"w":ws,"page":r["page"],"L":pages.get(r["page"],{}).get("L","?")})
def lcp(a,b):
    ga,gb=metrics.merge(a),metrics.merge(b); n=0
    for x,y in zip(ga,gb):
        if x!=y: break
        n+=1
    return n
def mean(xs): return sum(xs)/len(xs) if xs else 0.0
def boot(xs,ys,n=500,seed=3):
    rnd=random.Random(seed); ds=[]
    for _ in range(n):
        a=mean([xs[rnd.randrange(len(xs))] for _ in range(len(xs))])
        b=mean([ys[rnd.randrange(len(ys))] for _ in range(len(ys))])
        ds.append(a-b)
    ds.sort(); return ds[int(.025*n)], ds[int(.975*n)]

print("="*76)
print("ОБЩИЙ НАЧАЛЬНЫЙ КУСОК — с доверительными интервалами")
print("="*76)
for lang in ("A","B"):
    ls=[l for l in LINES if l["L"]==lang]
    rnd=random.Random(9); pool=[w for l in ls for w in l["w"]]; firsts=[l["w"][0] for l in ls]
    wr=[lcp(a,b) for l in ls for a,b in zip(l["w"],l["w"][1:])]
    wc=[lcp(a,rnd.choice(pool)) for l in ls for a in l["w"][:-1]]
    ar=[]; ac=[]
    for i in range(len(ls)-1):
        if ls[i+1]["page"]!=ls[i]["page"]: continue
        ar.append(lcp(ls[i]["w"][-1], ls[i+1]["w"][0])); ac.append(lcp(ls[i]["w"][-1], rnd.choice(firsts)))
    lw,hw=boot(wr,wc); la,ha=boot(ar,ac)
    z="ноль ВНУТРИ интервала" if la<=0<=ha else "ноль вне интервала"
    print(f"  {lang}: внутри строки избыток {mean(wr)-mean(wc):+.4f} [{lw:+.4f},{hw:+.4f}]")
    print(f"     через перенос избыток {mean(ar)-mean(ac):+.4f} [{la:+.4f},{ha:+.4f}]  → {z}\n")

print("="*76)
print("СПАД ПОХОЖЕСТИ С РАССТОЯНИЕМ ВНУТРИ СТРОКИ (общий начальный кусок)")
print("="*76)
for lang in ("A","B"):
    ls=[l for l in LINES if l["L"]==lang]
    rnd=random.Random(4); pool=[w for l in ls for w in l["w"]]
    base=mean([lcp(a,rnd.choice(pool)) for l in ls for a in l["w"][:-1]])
    out=[]
    for d in (1,2,3,4,5):
        v=[lcp(l["w"][i], l["w"][i+d]) for l in ls for i in range(len(l["w"])-d)]
        out.append((d, mean(v)-base, len(v)))
    # то же через границу строки, расстояние 1
    ar=[]; ac=[]
    firsts=[l["w"][0] for l in ls]
    for i in range(len(ls)-1):
        if ls[i+1]["page"]!=ls[i]["page"]: continue
        ar.append(lcp(ls[i]["w"][-1], ls[i+1]["w"][0])); ac.append(lcp(ls[i]["w"][-1], rnd.choice(firsts)))
    print(f"  {lang}:  " + "   ".join(f"d={d} {e:+.3f}" for d,e,_ in out) +
          f"   ‖ через перенос (d=1) {mean(ar)-mean(ac):+.3f}")
