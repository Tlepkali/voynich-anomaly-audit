# -*- coding: utf-8 -*-
import json, collections, math, statistics as st
D=json.load(open("parsed.json"))
LN=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
LN=[l for l in LN if len(l)>=4]
voc=collections.Counter(w for l in LN for w in l)
def positions(pred):
    ps=[]
    for l in LN:
        n=len(l)-1
        for i,w in enumerate(l):
            if pred(w,i,l): ps.append(i/n if n else 0)
    return ps
print("="*104)
print("ПОЗИЦИОННОЕ НАПИСАНИЕ: голый токен против слитной формы, место в строке")
print("="*104)
print(f"  {'элем':>5s} {'голых':>6s} {'место':>6s} {'1/5':>5s} | {'слитных':>8s} {'место':>6s} {'1/5':>5s} | {'сдвиг':>6s} {'z':>6s}")
rows=[]
for e in ("s","y","d","o","l","r","q","k","t","a","ch","sh"):
    bare=positions(lambda w,i,l,e=e: w==e)
    if len(bare)<40: 
        rows.append((None,e,len(bare),0)); continue
    # слитные: слово начинается с e, остаток — существующее слово длиной ≥2
    joined=positions(lambda w,i,l,e=e: w.startswith(e) and len(w)>len(e)+1 and w[len(e):] in voc and voc[w[len(e):]]>=20)
    if len(joined)<40:
        rows.append((None,e,len(bare),len(joined))); continue
    mb,mj=st.mean(bare),st.mean(joined)
    fb=sum(1 for p in bare if p<0.2)/len(bare)
    fj=sum(1 for p in joined if p<0.2)/len(joined)
    # z для разности долей «в первой пятой»
    p=(sum(1 for x in bare if x<0.2)+sum(1 for x in joined if x<0.2))/(len(bare)+len(joined))
    se=math.sqrt(max(1e-12,p*(1-p)*(1/len(bare)+1/len(joined))))
    z=(fj-fb)/se
    rows.append(((fj-fb,z,mb,mj,fb,fj,len(bare),len(joined)),e,len(bare),len(joined)))
for r,e,nb,nj in rows:
    if r is None:
        print(f"  {e:>5s} {nb:6d} {'—':>6s} {'—':>5s} | {nj:8d} {'—':>6s} {'—':>5s} |   данных мало")
        continue
    d,z,mb,mj,fb,fj,nb,nj=r
    mark="  ←" if e=="s" else ("  ЗНАЧИМО" if z>4 else "")
    print(f"  {e:>5s} {nb:6d} {mb:6.2f} {fb:5.0%} | {nj:8d} {mj:6.2f} {fj:5.0%} | {d:+5.0%} {z:6.1f}{mark}")
print("\n  «место» 0 = начало строки, 1 = конец;  «1/5» — доля в первой пятой строки")
print("  «сдвиг» — насколько чаще слитная форма стоит в начале строки, чем голая")
