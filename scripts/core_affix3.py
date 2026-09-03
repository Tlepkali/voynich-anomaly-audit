# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys
exec(open("scripts/core_affix.py").read().split("CORP=[")[0])
NC=1800
def shape_of(T):
    T=set(T); nb=nbrs(T)
    def m(d):
        g=[len(nb.get(w,())) for w in T if len(w)==d]
        return st.mean(g) if len(g)>=12 else float('nan')
    a,b=m(3),m(5)
    return (b/a if a==a and b==b and a>0 else float('nan'))
def avg_shape(pool,reps=25,seed=400):
    v=[]
    for s in range(reps):
        rnd=random.Random(seed+s)
        if len(pool)<NC: return float('nan')
        r=shape_of(rnd.sample(list(pool),NC))
        if r==r: v.append(r)
    return st.mean(v) if v else float('nan')
T=topN(VOY); d,cores,dep,P,U=decompose(T)
print("="*106); print("ЗАЩИТА ОТ КРУГОВОГО ВЫВОДА: не механика ли это удаления слов, у которых есть близкий сосед"); print("="*106)
base=avg_shape(T); real=avg_shape(cores)
print(f"  все {len(T)} типов                                     дл5/дл3 = {base:.2f}")
print(f"  {len(cores)} ЯДЕР (снят настоящий обвес, {len(d)/len(T):.0%} выведено)     дл5/дл3 = {real:.2f}   сдвиг {real-base:+.2f}")
nb=nbrs(set(T)); conn=[w for w in T if len(nb.get(w,()))>0]
k=len(d)
print(f"\n  КОНТРОЛЬ 1: удалить столько же ({k}) СЛУЧАЙНЫХ типов, у которых есть сосед на расстоянии 1")
print(f"              (таких типов всего {len(conn)}) — 12 повторов")
vals=[]
for s in range(12):
    rnd=random.Random(500+s)
    drop=set(rnd.sample(conn,min(k,len(conn))))
    r=avg_shape([w for w in T if w not in drop],reps=8,seed=600+s*13)
    if r==r: vals.append(r)
print(f"              дл5/дл3 = {st.mean(vals):.2f} (разброс {min(vals):.2f}–{max(vals):.2f})   сдвиг {st.mean(vals)-base:+.2f}")
print(f"\n  КОНТРОЛЬ 2: тот же алгоритм, но приставки и окончания выбраны СЛУЧАЙНО, а не по частоте")
allp=collections.Counter(); alls=collections.Counter()
for w in T:
    for L in (1,2,3):
        if len(w)>L: allp[w[:L]]+=1; alls[w[-L:]]+=1
cand_p=[a for a,n in allp.items() if n>=20]; cand_s=[a for a,n in alls.items() if n>=20]
vals2=[]; ders=[]
S=set(T)
for s in range(12):
    rnd=random.Random(700+s)
    RP=rnd.sample(cand_p,min(K_AFF,len(cand_p))); RS=rnd.sample(cand_s,min(K_AFF,len(cand_s)))
    der=set()
    for w in S:
        if any(w.startswith(a) and w[len(a):] in S and len(w[len(a):])>=2 for a in RP) or \
           any(w.endswith(a) and w[:-len(a)] in S and len(w[:-len(a)])>=2 for a in RS): der.add(w)
    cc=[w for w in S if w not in der]; ders.append(len(der)/len(S))
    if len(cc)>=NC:
        r=avg_shape(cc,reps=8,seed=800+s*17)
        if r==r: vals2.append(r)
print(f"              выведено {st.mean(ders):.0%} (против {len(d)/len(T):.0%} у частотных приставок)")
if vals2: print(f"              дл5/дл3 = {st.mean(vals2):.2f} (разброс {min(vals2):.2f}–{max(vals2):.2f})   сдвиг {st.mean(vals2)-base:+.2f}")
print(f"\n  КОНТРОЛЬ 3: удалить {k} типов с НАИБОЛЬШИМ числом соседей (заведомо максимальный механический эффект)")
worst=set(sorted(T,key=lambda w:-len(nb.get(w,())))[:k])
r3=avg_shape([w for w in T if w not in worst],reps=12,seed=900)
print(f"              дл5/дл3 = {r3:.2f}   сдвиг {r3-base:+.2f}")
