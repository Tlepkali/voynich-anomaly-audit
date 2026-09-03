import json, random, sys, collections
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
SEC={"T":"текст","H":"травник","A":"астрон.","Z":"зодиак","B":"«банный»",
     "C":"космол.","P":"аптечный","S":"рецепты"}
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
def g0(w): return metrics.merge(w)[0]
def mean(x): return sum(x)/len(x) if x else 0.0

def d2_per_line(ls):
    out=[]
    for l in ls:
        w=l["w"]; v=[lcp(w[i],w[i+2])-lcp(w[i],w[i+1]) for i in range(len(w)-2)]
        if v: out.append(mean(v))
    return out
def boot(v,n=3000,seed=19):
    if len(v)<40: return None
    rnd=random.Random(seed); N=len(v); r=[]
    for _ in range(n): r.append(sum(v[rnd.randrange(N)] for _ in range(N))/N)
    r.sort(); return mean(v), r[int(.025*n)], r[int(.975*n)]
def bundle(ls):
    pool=[w for l in ls for w in l["w"]]; rnd=random.Random(3)
    fi=collections.Counter(g0(l["w"][0]) for l in ls)
    mi=collections.Counter(g0(w) for l in ls for w in l["w"][1:-1])
    Tf=sum(fi.values()); Tm=sum(mi.values()) or 1
    div=0.5*sum(abs(fi.get(k,0)/Tf-mi.get(k,0)/Tm) for k in set(fi)|set(mi))
    m=mean([1 if l["w"][-1].endswith('m') else 0 for l in ls])
    adj=mean([lcp(a,b) for l in ls for a,b in zip(l["w"],l["w"][1:])])
    ctl=mean([lcp(a,rnd.choice(pool)) for l in ls for a in l["w"][:-1]])
    return div, m, adj-ctl

CELLS=[("рука 1","H","A"),("рука 1","P","A"),
       ("рука 2","B","B"),("рука 2","H","B"),("рука 2","T","B"),("рука 2","C","B"),
       ("рука 3","S",None),("рука 3","H",None),("рука 5","H","B")]
def sel(h,s,L):
    return [l for l in LINES if l["H"]==h.split()[-1] and l["I"]==s and (L is None or l["L"]==L)]

print("="*98)
print("ЯЧЕЙКИ рука × раздел: четыре меры строчной структуры")
print("="*98)
print(f"  {'ячейка':26s} {'яз':3s} {'строк':>6s} {'эффект d=2':>22s} {'нач.строки':>11s} {'m в конце':>10s} {'копирование':>12s}")
for h,s,L in CELLS:
    ls=sel(h,s,L)
    if len(ls)<55: continue
    b=boot(d2_per_line(ls)); div,mr,cp=bundle(ls)
    lang="".join(sorted({l["L"] for l in ls}))
    d2s = f"{b[0]:+.3f} [{b[1]:+.3f},{b[2]:+.3f}]" if b else "мало"
    print(f"  {h+' · '+SEC.get(s,s):26s} {lang:3s} {len(ls):6d} {d2s:>22s} {div:11.3f} {mr:10.1%} {cp:12.3f}")

print("\n"+"="*98)
print("ПРЯМЫЕ СРАВНЕНИЯ (бутстрэп разности по строкам)")
print("="*98)
def diff(a,b,label,n=4000,seed=91):
    da,db=d2_per_line(a),d2_per_line(b)
    if len(da)<40 or len(db)<40: print(f"  {label:46s} мало данных"); return
    rnd=random.Random(seed); r=[]
    for _ in range(n):
        r.append(sum(da[rnd.randrange(len(da))] for _ in range(len(da)))/len(da)
                -sum(db[rnd.randrange(len(db))] for _ in range(len(db)))/len(db))
    r.sort(); lo,hi=r[int(.025*n)],r[int(.975*n)]
    mark="различаются ✓" if (lo>0 or hi<0) else "не различаются ·"
    print(f"  {label:46s} {mean(da)-mean(db):+.4f} [{lo:+.4f}, {hi:+.4f}]  {mark}")

print("  — НОВОЕ: разделы внутри одной руки в языке A —")
diff(sel("рука 1","H","A"), sel("рука 1","P","A"), "рука 1: травник − аптечный")
print("  — разделы внутри руки 2 (язык B) —")
diff(sel("рука 2","B","B"), sel("рука 2","H","B"), "рука 2: «банный» − травник")
diff(sel("рука 2","B","B"), sel("рука 2","T","B"), "рука 2: «банный» − только текст")
diff(sel("рука 2","T","B"), sel("рука 2","H","B"), "рука 2: только текст − травник")
print("  — ОДИН РАЗДЕЛ, РАЗНЫЕ РУКИ И ЯЗЫКИ: травник —")
diff(sel("рука 1","H","A"), sel("рука 2","H","B"), "травник: рука 1 (яз. A) − рука 2 (яз. B)")
diff(sel("рука 2","H","B"), [l for l in LINES if l["I"]=="H" and l["H"] in ("3","5")],
     "травник: рука 2 − руки 3 и 5 (все яз. B)")
print("  — ТОТ ЖЕ ПИСЕЦ, ТОТ ЖЕ РАЗДЕЛ, РАЗНЫЙ ЯЗЫК —")
diff([l for l in LINES if l["H"]=="3" and l["I"]=="S" and l["L"]=="A"],
     [l for l in LINES if l["H"]=="3" and l["I"]=="S" and l["L"]=="B"],
     "рука 3, рецепты: язык A − язык B")
