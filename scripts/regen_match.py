# -*- coding: utf-8 -*-
"""Зависит ли главное сравнение §5.1 от способа выравнивания словаря.
Два защищаемых способа:
  A. случайная выборка нужного числа типов со средней длиной как у рукописи (regen2.pair)
  B. выборка, повторяющая ВСЁ распределение длин рукописи, а не только среднее (regen.match_lengths)
Оба по 5 зёрен выборки × 3 зерна цепи."""
import json, collections, random, statistics as st, math, os
exec(open("scripts/density_null2.py").read().split('print("="*100)')[0])
src=open("scripts/regen.py",encoding="utf-8").read()
exec(src[src.index("def match_lengths"):src.index("def load_types")])
VL=load(); TV=sorted({w for l in VL for w in l}); VLENS=[len(w) for w in TV]
mV=st.mean(len(w) for w in TV)
def pair(T,n,target_mean,seed=0,tol=0.25):
    rnd=random.Random(seed); best=None
    for _ in range(400):
        s=rnd.sample(T,min(n,len(T))); m=st.mean(len(w) for w in s)
        if abs(m-target_mean)<tol: return sorted(s)
        if best is None or abs(m-target_mean)<best[0]: best=(abs(m-target_mean),s)
    return sorted(best[1])
vv=st.mean(regen(TV,2,s)[0] for s in range(5))
print("="*104); print(f"РУКОПИСЬ: {len(TV)} типов, ср. длина {mV:.2f}, порождение {vv:.1%} (5 зёрен)"); print("="*104)
print(f"  {'корпус':>13s} {'способ':>44s} {'типов':>6s} {'ср.дл':>6s} {'доля':>7s} {'разброс':>13s} {'к рукописи':>11s}")
for lab,fn in [("латынь","latin.clean"),("испанский","bk_es.clean"),("итальянский","bk_it.clean")]:
    T=sorted(set(open("ref/"+fn,encoding="utf-8",errors="ignore").read().split()))
    for nm,mk in [("A: случайная выборка, средняя длина как цель",
                   lambda sd: pair([w for w in T if len(w)<=int(mV)+3],len(TV),mV,seed=sd)),
                  ("B: выборка по всему распределению длин",
                   lambda sd: match_lengths(T,VLENS,len(TV),seed=sd))]:
        vals=[]; ns=[]; ms=[]
        for sd in range(5):
            M=mk(sd); ns.append(len(M)); ms.append(st.mean(len(w) for w in M))
            vals+= [regen(M,2,cs)[0] for cs in range(3)]
        print(f"  {lab:>13s} {nm:>44s} {int(st.mean(ns)):6d} {st.mean(ms):6.2f} {st.mean(vals):6.1%} [{min(vals):5.1%};{max(vals):5.1%}] {vv/st.mean(vals):10.1f}×")
