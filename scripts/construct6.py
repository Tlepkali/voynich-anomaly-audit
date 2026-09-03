# -*- coding: utf-8 -*-
"""Проверка пятой архитектуры: пять зёрен на победившей точке и решётка."""
import json, collections, random, statistics as st, math
exec(open("scripts/construct5.py").read().split('print("="*100)')[0])
def run(args, seeds):
    ds=[battery(arch5(*args,seed=s),"") for s in range(seeds)]
    return {k:(st.mean(d[k] for d in ds), st.stdev(d[k] for d in ds) if len(ds)>1 else 0) for k in ("r1","la","rc","j")}
print("="*100); print("ПОБЕДИВШАЯ ТОЧКА НА ПЯТИ ЗЁРНАХ"); print("="*100)
m=run((0.15,0.10,0.20),5)
print(f"  {'мера':>18s} {'значение':>16s} {'доля цели':>10s} {'≥70 %':>7s}")
for k,nm in [("r1","возврат d1-5"),("la","автокорреляция"),("rc","ранг-корреляция"),("j","стык")]:
    f=m[k][0]/T[k]
    print(f"  {nm:>18s} {m[k][0]:9.3f}±{m[k][1]:.3f} {f:9.0%} {'ДА' if f>=0.70 else 'нет':>7s}")
print(f"\n  все четыре взяты: {'ДА' if all(m[k][0]/T[k]>=0.70 for k in ('r1','la','rc','j')) else 'НЕТ'}")
print("\n"+"="*100); print("РЕШЁТКА: сколько точек берут все четыре (порог 70 %, 2 зерна)"); print("="*100)
G=[0.05,0.15,0.25,0.35]
pts=[(a,b,c) for a in G for b in G for c in [0.0,0.10,0.20,0.30] if a+b+c<=0.75]
print(f"  точек: {len(pts)}")
cnt=collections.Counter(); wins=[]
for p in pts:
    mm=run(p,2); k=sum(1 for x in ("r1","la","rc","j") if mm[x][0]/T[x]>=0.70)
    cnt[k]+=1
    if k==4: wins.append((p,{x:mm[x][0]/T[x] for x in ("r1","la","rc","j")}))
for k in sorted(cnt,reverse=True): print(f"  {k} из 4: {cnt[k]:3d}")
print(f"\n  ВЗЯЛИ ВСЕ ЧЕТЫРЕ: {len(wins)} точек")
for p,f in wins[:6]:
    print(f"    сосед {p[0]:.2f} кеш {p[1]:.2f} частота {p[2]:.2f} → "+" ".join(f"{k} {v:.0%}" for k,v in f.items()))
