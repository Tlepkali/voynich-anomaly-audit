# -*- coding: utf-8 -*-
import json, collections, math, statistics as st
D=json.load(open("parsed.json"))
LN=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
LN=[l for l in LN if len(l)>=5]
voc=collections.Counter(w for l in LN for w in l)
def occ():
    o=collections.defaultdict(list)
    for l in LN:
        n=len(l)-1
        for i,w in enumerate(l): o[w].append(i/n if n else 0)
    return o
O=occ()
def test(P, minb=15, minx=25):
    """для каждой основы X: доля слитных PX среди {X, PX} по пятым долям строки"""
    bases=[X for X,n in voc.items() if n>=minx and voc.get(P+X,0)>=minb]
    if len(bases)<4: return None
    bins=[[0,0] for _ in range(5)]        # [слитных, всего]
    per=[]
    for X in bases:
        b=[[0,0] for _ in range(5)]
        for p in O[X]:
            k=min(int(p*5),4); b[k][1]+=1
        for p in O[P+X]:
            k=min(int(p*5),4); b[k][0]+=1; b[k][1]+=1
        for k in range(5):
            bins[k][0]+=b[k][0]; bins[k][1]+=b[k][1]
        f=[b[k][0]/b[k][1] if b[k][1]>=5 else None for k in range(5)]
        if f[0] is not None and f[4] is not None: per.append(f[0]-f[4])
    fr=[bins[k][0]/bins[k][1] if bins[k][1] else 0 for k in range(5)]
    a0,n0=bins[0]; a4,n4=bins[4]
    p1,p2=a0/n0,a4/n4
    pp=(a0+a4)/(n0+n4)
    se=math.sqrt(max(1e-12,pp*(1-pp)*(1/n0+1/n4)))
    z=(p1-p2)/se
    up=sum(1 for d in per if d>0)
    return fr, bins, z, len(bases), up, len(per)
print("="*106)
print("ДОЛЯ СЛИТНЫХ ФОРМ ВДОЛЬ СТРОКИ ПРИ ФИКСИРОВАННОЙ ОСНОВЕ")
print("(не зависит от того, где стоят сами основы)")
print("="*106)
print(f"  {'P':>5s} {'основ':>6s} | " + " ".join(f"{'пятая '+str(k+1):>9s}" for k in range(5)) + f" | {'z':>6s} {'основ ↓':>9s}")
for P in ("s","sh","q","ch","qo","y","d","o","che","she","qok","ot","ok"):
    r=test(P)
    if r is None:
        print(f"  {P:>5s} {'—':>6s} |   основ мало")
        continue
    fr,bins,z,nb,up,npair=r
    mark=""
    if z>3: mark="  ← СПАДАЕТ"
    elif z<-3: mark="  растёт"
    print(f"  {P:>5s} {nb:6d} | " + " ".join(f"{f:9.1%}" for f in fr) + f" | {z:6.1f} {str(up)+'/'+str(npair):>9s}{mark}")
print("\n  «спадает» = слитная форма чаще в начале строки, чем в конце — признак позиционного написания")
print("  «основ ↓» — у скольких основ доля падает от первой пятой к последней")
