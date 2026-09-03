# -*- coding: utf-8 -*-
"""Чувствительность к порогу. Главное утверждение генеративной статьи держится
на отсечке 70 %, названной произвольной и ни разу не проверенной.
Плюс мера без отсечки: максимум ХУДШЕЙ из четырёх долей."""
import json, collections, random, statistics as st, math
exec(open("scripts/construct5.py").read().split('print("="*100)')[0])
def run(args, seeds=2):
    ds=[battery(arch5(*args,seed=s),"") for s in range(seeds)]
    return {k:st.mean(d[k] for d in ds) for k in ("r1","la","rc","j")}
G=[0.05,0.15,0.25,0.35]
pts=[(a,b,c) for a in G for b in G for c in [0.0,0.10,0.20,0.30] if a+b+c<=0.75]
print(f"конфигураций: {len(pts)}, по два зерна")
R=[]
for p in pts:
    m=run(p); f={k:m[k]/T[k] for k in ("r1","la","rc","j")}
    R.append((p,f,min(f.values())))
R.sort(key=lambda x:-x[2])
print("\n"+"="*96); print("СКОЛЬКО КОНФИГУРАЦИЙ БЕРУТ ВСЕ ЧЕТЫРЕ ПРИ РАЗНЫХ ПОРОГАХ"); print("="*96)
print(f"  {'порог':>7s} {'конфигураций':>14s} {'доля решётки':>14s}")
for thr in (0.60,0.65,0.70,0.75,0.80,0.85,0.90):
    n=sum(1 for _,f,w in R if w>=thr)
    print(f"  {thr:6.0%} {n:14d} {n/len(R):13.0%}")
print("\n"+"="*96); print("БЕЗ ОТСЕЧКИ: конфигурации по МАКСИМУМУ ХУДШЕЙ ИЗ ЧЕТЫРЁХ ДОЛЕЙ"); print("="*96)
print(f"  {'сосед':>6s} {'кеш':>5s} {'част':>5s} | {'возврат':>8s} {'автокорр':>9s} {'ранг':>7s} {'стык':>7s} | {'ХУДШАЯ':>7s}")
for p,f,w in R[:8]:
    print(f"  {p[0]:6.2f} {p[1]:5.2f} {p[2]:5.2f} | {f['r1']:7.0%} {f['la']:8.0%} {f['rc']:6.0%} {f['j']:6.0%} | {w:6.0%}")
print(f"\n  лучшая худшая доля по всей решётке: {R[0][2]:.0%}")
print(f"  медиана худшей доли: {st.median([w for _,_,w in R]):.0%}")
bad=collections.Counter()
for _,f,w in R:
    bad[min(f,key=f.get)]+=1
print(f"\n  какая мера чаще всего оказывается худшей: "+", ".join(f"{k} {v}" for k,v in bad.most_common()))
