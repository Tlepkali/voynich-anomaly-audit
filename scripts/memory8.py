# -*- coding: utf-8 -*-
"""Доступен ли механизм соседа языкам, и что даёт связка сосед + кеш."""
import json, collections, random, statistics as st, math
exec(open("scripts/memory7.py").read().split('print(f"типов')[0])
TYPES=sorted(set(VOY)); NB=nbr_map(TYPES)
print("="*100); print("ДОСТУПНОСТЬ МЕХАНИЗМА: у какой доли типов вообще есть сосед"); print("="*100)
print(f"  {'корпус':>16s} {'типов':>7s} {'имеют соседа':>14s} {'соседей на тип':>15s}")
rows=[("Войнич",TYPES)]
import os
for fn,lab in [("latin.clean","латынь"),("bk_es.clean","испанский"),("bk_it.clean","итальянский")]:
    if os.path.exists("ref/"+fn):
        w=open(f"ref/{fn}",encoding="utf-8",errors="ignore").read().split()
        rows.append((lab, sorted(set(w))))
for lab,T2 in rows:
    nb=nbr_map(T2) if lab!="Войнич" else NB
    have=sum(1 for w in T2 if nb.get(w))
    dens=st.mean(len(nb.get(w,())) for w in T2)
    print(f"  {lab:>16s} {len(T2):7d} {have/len(T2):13.1%} {dens:15.2f}")
print("\n  механизм «выдай соседа» требует, чтобы у слова БЫЛ сосед. У рукописи он есть")
print("  у 85 % типов, у языков — у меньшинства. Это не настройка, а доступность.")
def combo_nb(pn, pc, wc, seed=0):
    """сосед предыдущего + кеш по тождеству"""
    rnd=random.Random(seed); bag=VOY[:]; rnd.shuffle(bag)
    out=[]; prev=None; q=collections.deque(maxlen=wc); i=0
    while len(out)<len(VOY) and i<len(bag):
        u=rnd.random()
        if prev is not None and u<pn and NB.get(prev):
            n=NB[prev]; x=n[rnd.randrange(len(n))]
        elif q and u<pn+pc: x=q[rnd.randrange(len(q))]
        else: x=bag[i]; i+=1
        out.append(x); prev=x; q.append(x)
    return cut(out[:len(VOY)])
T=battery(VL,"РУКОПИСЬ")
def multi(args, seeds=4):
    ds=[battery(combo_nb(*args, seed=s), "") for s in range(seeds)]
    return {k:(st.mean(d[k] for d in ds), st.stdev(d[k] for d in ds)) for k in ("r1","r2","la","rc","j")}
print("\n"+"="*100); print("СОСЕД + КЕШ (подгонка по возврату и автокорреляции; ранг и стык отложены)"); print("="*100)
print(f"  {'p_сос':>6s} {'p_кеш':>6s} {'w':>4s} {'возв d1-5':>12s} {'d6-20':>11s} {'автокорр':>14s} | {'РАНГ':>15s} {'СТЫК':>12s}")
print(f"  {'ЦЕЛЬ':>6s} {'':>6s} {'':>4s} {T['r1']:12.2f} {T['r2']:11.2f} {T['la']:+14.3f} | {T['rc']:+15.4f} {T['j']:12.3f}")
res=[]
for pn in (0.10,0.15,0.20):
    for pc in (0.10,0.15):
        for wc in (40,100):
            m=multi((pn,pc,wc))
            e=abs(m['r1'][0]-T['r1'])/T['r1']+abs(m['r2'][0]-T['r2'])/T['r2']+abs(m['la'][0]-T['la'])/abs(T['la'])
            res.append((e,pn,pc,wc,m))
res.sort(key=lambda x:x[0])
for e,pn,pc,wc,m in res[:5]:
    f=lambda k,fmt: f"{fmt%m[k][0]}±{m[k][1]:.3f}"
    print(f"  {pn:6.2f} {pc:6.2f} {wc:4d} {f('r1','%.2f'):>12s} {f('r2','%.2f'):>11s} {f('la','%+.3f'):>14s} | {f('rc','%+.4f'):>15s} {f('j','%.3f'):>12s}")
