# -*- coding: utf-8 -*-
"""Четвёртая память — над ГРАНИЦЕЙ: выбор следующего слова зависит от последнего
знака предыдущего. Совместима ли она с тремя словесными."""
import json, collections, random, statistics as st, math
exec(open("scripts/memory5.py").read().split('def err3')[0])
BYFIRST=collections.defaultdict(list)
for w in VOY: BYFIRST[w[0]].append(w)
# наблюдённое распределение первого знака при данном последнем
TRANS=collections.defaultdict(collections.Counter)
for l in VL:
    for a,b in zip(l,l[1:]): TRANS[a[-1]][b[0]]+=1
POOLS={k:[c for c,n in v.items() for _ in range(n)] for k,v in TRANS.items()}
def combo4(pc, wc, al, ar, ab, seed=0):
    rnd=random.Random(seed); q=collections.deque(maxlen=wc)
    out=[]; pl=None; pr=None; plast=None
    for _ in range(len(VOY)):
        u=rnd.random()
        if plast is not None and u<ab and POOLS.get(plast):
            ch=POOLS[plast][rnd.randrange(len(POOLS[plast]))]
            pool=BYFIRST.get(ch)
            x=pool[rnd.randrange(len(pool))] if pool else VOY[rnd.randrange(len(VOY))]
        elif q and u<ab+pc: x=q[rnd.randrange(len(q))]
        elif pr is not None and u<ab+pc+ar and BYCLS[pr]: x=BYCLS[pr][rnd.randrange(len(BYCLS[pr]))]
        elif pl is not None and u<ab+pc+ar+al:
            cand=[k for k in (pl-1,pl,pl+1) if k in BYLEN]
            L=cand[rnd.randrange(len(cand))]; x=BYLEN[L][rnd.randrange(len(BYLEN[L]))]
        else:
            L=LENS_POOL[rnd.randrange(len(LENS_POOL))]; x=BYLEN[L][rnd.randrange(len(BYLEN[L]))]
        out.append(x); q.append(x); pl=len(x); pr=CLS[x]; plast=x[-1]
    return cut(out)
print("="*104); print("ЧЕТВЁРТАЯ ПАМЯТЬ — НАД ГРАНИЦЕЙ СЛОВА"); print("="*104)
print(f"  {'ab':>5s} {'возв d1-5':>10s} {'автокорр':>9s} {'ранг-корр':>10s} {'стык':>8s} {'соседство':>10s}")
print(f"  {'ЦЕЛЬ':>5s} {T['r1']:10.2f} {T['la']:+9.3f} {T['rc']:+10.4f} {T['j']:8.3f} {T['adj']:9.2f}×")
print(f"  {'0':>5s} — три словесные памяти, лучший набор pc=0.15 wc=40 al=0.10 ar=0.10:")
d0=battery(combo(0.15,40,0.10,0.10,0), "")
print(f"  {'':>5s} {d0['r1']:10.2f} {d0['la']:+9.3f} {d0['rc']:+10.4f} {d0['j']:8.3f} {d0['adj']:9.2f}×")
print()
for ab in (0.1,0.2,0.35,0.5,0.7):
    d=battery(combo4(0.15,40,0.10,0.10,ab,0), "")
    print(f"  {ab:5.2f} {d['r1']:10.2f} {d['la']:+9.3f} {d['rc']:+10.4f} {d['j']:8.3f} {d['adj']:9.2f}×")
print("\n  вопрос: приходит ли стык и что при этом ломается")
