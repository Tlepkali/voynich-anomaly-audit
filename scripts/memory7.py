# -*- coding: utf-8 -*-
"""Пятый механизм: следующее слово — ПОЧТИ-ДВОЙНИК предыдущего (расстояние 1).
Доступен только при плотном словаре, то есть рукописи, но не латыни.
УСЛОВИЯ ДО ЗАПУСКА: подгонка ТОЛЬКО по профилю возврата;
отложены — автокорреляция длины, ранг-корреляция соседей, стык по 1 знаку.
Все конфигурации — на пяти зёрнах, приводится среднее ± разброс."""
import json, collections, random, statistics as st, math
exec(open("scripts/memory.py").read().split('print("="*112)')[0])
T=battery(VL,"РУКОПИСЬ")
def nbr_map(types):
    idx=collections.defaultdict(set)
    for w in types:
        for i in range(len(w)): idx[w[:i]+w[i+1:]].add(w)
        idx[w].add(w)
    nb=collections.defaultdict(set)
    for _,ws in idx.items():
        ws=list(ws)
        for i in range(len(ws)):
            for j in range(i+1,len(ws)):
                a,b=ws[i],ws[j]
                if a!=b and abs(len(a)-len(b))<=1: nb[a].add(b); nb[b].add(a)
    return {k:sorted(v) for k,v in nb.items()}
TYPES=sorted(set(VOY)); NB=nbr_map(TYPES)
have=sum(1 for w in TYPES if NB.get(w))
print(f"типов {len(TYPES)}, из них имеют соседа {have} = {have/len(TYPES):.1%}")
def neighbour_model(p, seed=0):
    rnd=random.Random(seed); bag=VOY[:]; rnd.shuffle(bag)
    out=[]; prev=None; i=0
    while len(out)<len(VOY) and i<len(bag):
        if prev is not None and rnd.random()<p and NB.get(prev):
            n=NB[prev]; x=n[rnd.randrange(len(n))]
        else:
            x=bag[i]; i+=1
        out.append(x); prev=x
    return cut(out[:len(VOY)])
def multi(fn, args, seeds=5):
    ds=[battery(fn(*args, seed=s), "") for s in range(seeds)]
    k=lambda key: (st.mean(d[key] for d in ds), st.stdev(d[key] for d in ds) if len(ds)>1 else 0)
    return {key:k(key) for key in ("r1","r2","tail","adj","la","rc","j")}
print("\n"+"="*110); print("ПЯТЫЙ МЕХАНИЗМ: сосед предыдущего слова (5 зёрен, среднее ± разброс)"); print("="*110)
print(f"  {'p':>5s} {'возврат d1-5':>15s} {'d6-20':>13s} | {'АВТОКОРР':>16s} {'РАНГ-КОРР':>17s} {'СТЫК':>15s}")
print(f"  {'ЦЕЛЬ':>5s} {T['r1']:15.2f} {T['r2']:13.2f} | {T['la']:+16.3f} {T['rc']:+17.4f} {T['j']:15.3f}")
best=None
for p in (0.05,0.10,0.15,0.20,0.30,0.45):
    m=multi(neighbour_model,(p,))
    e=abs(m['r1'][0]-T['r1'])/T['r1']+abs(m['r2'][0]-T['r2'])/T['r2']
    if best is None or e<best[0]: best=(e,p,m)
    f=lambda k,fmt: f"{fmt%m[k][0]}±{m[k][1]:.3f}" if m[k][1]<1 else f"{fmt%m[k][0]}±{m[k][1]:.1f}"
    print(f"  {p:5.2f} {f('r1','%.2f'):>15s} {f('r2','%.2f'):>13s} | {f('la','%+.3f'):>16s} {f('rc','%+.4f'):>17s} {f('j','%.3f'):>15s}")
e,p,m=best
print(f"\n  ЛУЧШИЙ ПО ВОЗВРАТУ: p={p}, ошибка {e:.3f}")
print(f"  отложенные при нём: автокорр {m['la'][0]:+.3f} / цель {T['la']:+.3f} = {m['la'][0]/T['la']:.0%}; "
      f"ранг {m['rc'][0]:+.4f} / {T['rc']:+.4f} = {m['rc'][0]/T['rc']:.0%}; "
      f"стык {m['j'][0]:.3f} / {T['j']:.3f} = {m['j'][0]/T['j']:.0%}")
