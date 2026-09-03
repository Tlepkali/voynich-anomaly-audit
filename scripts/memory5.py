# -*- coding: utf-8 -*-
"""Три памяти сразу: кеш по тождеству + притяжение по длине + притяжение по классу
частоты. Совместимы ли они, или тянут друг против друга.
ОТЛОЖЕНО И НЕ ПОДГОНЯЕТСЯ: стык по 1 знаку."""
import json, collections, random, statistics as st, math
exec(open("scripts/memory.py").read().split('print("="*112)')[0])
T=battery(VL,"РУКОПИСЬ")
c=collections.Counter(VOY); order=[w for w,_ in c.most_common()]
NB=6; step=max(1,len(order)//NB)
CLS={w:min(i//step,NB-1) for i,w in enumerate(order)}
BYLEN=collections.defaultdict(list); BYCLS=collections.defaultdict(list)
for w in VOY: BYLEN[len(w)].append(w); BYCLS[CLS[w]].append(w)
LENS_POOL=[len(w) for w in VOY]
def combo(pc, wc, al, ar, seed=0):
    """pc,wc — кеш по тождеству; al — притяжение по длине; ar — по классу частоты"""
    rnd=random.Random(seed); q=collections.deque(maxlen=wc)
    out=[]; pl=None; pr=None
    for _ in range(len(VOY)):
        u=rnd.random()
        if q and u<pc:
            x=q[rnd.randrange(len(q))]
        elif pr is not None and u<pc+ar and BYCLS[pr]:
            x=BYCLS[pr][rnd.randrange(len(BYCLS[pr]))]
        elif pl is not None and u<pc+ar+al:
            cand=[k for k in (pl-1,pl,pl+1) if k in BYLEN]
            L=cand[rnd.randrange(len(cand))]
            x=BYLEN[L][rnd.randrange(len(BYLEN[L]))]
        else:
            L=LENS_POOL[rnd.randrange(len(LENS_POOL))]
            x=BYLEN[L][rnd.randrange(len(BYLEN[L]))]
        out.append(x); q.append(x); pl=len(x); pr=CLS[x]
    return cut(out)
def err3(d):
    return (abs(d['r1']-T['r1'])/T['r1'] + abs(d['la']-T['la'])/abs(T['la'])
            + abs(d['rc']-T['rc'])/abs(T['rc']))
print("="*108); print("ТРИ ПАМЯТИ СРАЗУ (подгонка по возврату, автокорреляции и ранг-корреляции)"); print("="*108)
print(f"  {'pc':>5s} {'wc':>4s} {'al':>5s} {'ar':>5s} {'возв d1-5':>10s} {'автокорр':>9s} {'ранг-корр':>10s} {'ошибка':>7s} | {'СТЫК':>7s} {'соседство':>10s}")
print(f"  {'—':>5s} {'—':>4s} {'—':>5s} {'—':>5s} {T['r1']:10.2f} {T['la']:+9.3f} {T['rc']:+10.4f} {'ЦЕЛЬ':>7s} | {T['j']:7.3f} {T['adj']:9.2f}×")
res=[]
for pc in (0.10,0.15):
    for wc in (40,100):
        for al in (0.05,0.10,0.15):
            for ar in (0.05,0.10,0.15):
                d=battery(combo(pc,wc,al,ar,0),"")
                res.append((err3(d),pc,wc,al,ar,d))
res.sort(key=lambda x:x[0])
for e,pc,wc,al,ar,d in res[:6]:
    print(f"  {pc:5.2f} {wc:4d} {al:5.2f} {ar:5.2f} {d['r1']:10.2f} {d['la']:+9.3f} {d['rc']:+10.4f} {e:7.3f} | {d['j']:7.3f} {d['adj']:9.2f}×")
e,pc,wc,al,ar,d=res[0]
print(f"\n  ЛУЧШАЯ: возврат {d['r1']:.2f}/{T['r1']:.2f}, автокорр {d['la']:+.3f}/{T['la']:+.3f}, "
      f"ранг {d['rc']:+.4f}/{T['rc']:+.4f}")
print(f"  ОТЛОЖЕННЫЙ СТЫК: {d['j']:.3f} против {T['j']:.3f} у рукописи — {d['j']/max(T['j'],1e-9)*100:.0f} % цели")
