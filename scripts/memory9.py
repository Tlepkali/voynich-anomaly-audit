# -*- coding: utf-8 -*-
"""Конкуренция памятей на ИСПРАВЛЕННОМ наборе: сосед + кеш + частота + граница.
УСЛОВИЯ ДО ЗАПУСКА: подгонка по возврату (d1-5, d6-20), автокорреляции длины и
ранг-корреляции; ОТЛОЖЕН — стык по 1 знаку."""
import json, collections, random, statistics as st, math
exec(open("scripts/memory7.py").read().split('print(f"типов')[0])
TYPES=sorted(set(VOY)); NB=nbr_map(TYPES)
T=battery(VL,"РУКОПИСЬ")
c=collections.Counter(VOY); order=[w for w,_ in c.most_common()]
NBC=6; step=max(1,len(order)//NBC)
CLS={w:min(i//step,NBC-1) for i,w in enumerate(order)}
BYCLS=collections.defaultdict(list)
for w in VOY: BYCLS[CLS[w]].append(w)
BYFIRST=collections.defaultdict(list)
for w in VOY: BYFIRST[w[0]].append(w)
TRANS=collections.defaultdict(collections.Counter)
for l in VL:
    for a,b in zip(l,l[1:]): TRANS[a[-1]][b[0]]+=1
POOLS={k:[ch for ch,n in v.items() for _ in range(n)] for k,v in TRANS.items()}
def model(pn, pc, wc, pr, pb, seed=0):
    """сосед / кеш / класс частоты / граница; остаток — из общего мешка"""
    rnd=random.Random(seed); bag=VOY[:]; rnd.shuffle(bag)
    out=[]; prev=None; q=collections.deque(maxlen=wc); i=0
    while len(out)<len(VOY) and i<len(bag):
        u=rnd.random(); x=None
        if prev is not None and u<pb and POOLS.get(prev[-1]):
            pl=POOLS[prev[-1]]; ch=pl[rnd.randrange(len(pl))]
            p2=BYFIRST.get(ch)
            if p2: x=p2[rnd.randrange(len(p2))]
        if x is None and prev is not None and u<pb+pn and NB.get(prev):
            n=NB[prev]; x=n[rnd.randrange(len(n))]
        if x is None and q and u<pb+pn+pc: x=q[rnd.randrange(len(q))]
        if x is None and prev is not None and u<pb+pn+pc+pr and BYCLS[CLS[prev]]:
            b=BYCLS[CLS[prev]]; x=b[rnd.randrange(len(b))]
        if x is None: x=bag[i]; i+=1
        out.append(x); prev=x; q.append(x)
    return cut(out[:len(VOY)])
def multi(args, seeds=3):
    ds=[battery(model(*args, seed=s), "") for s in range(seeds)]
    return {k:(st.mean(d[k] for d in ds), (st.stdev(d[k] for d in ds) if len(ds)>1 else 0)) for k in ("r1","r2","la","rc","j")}
def err(m):
    return (abs(m['r1'][0]-T['r1'])/T['r1']+abs(m['r2'][0]-T['r2'])/T['r2']
            +abs(m['la'][0]-T['la'])/abs(T['la'])+abs(m['rc'][0]-T['rc'])/abs(T['rc']))
print("="*112); print("КОНКУРЕНЦИЯ НА ИСПРАВЛЕННОМ НАБОРЕ (стык отложен и не подгоняется)"); print("="*112)
print(f"  {'сосед':>6s} {'кеш':>5s} {'част':>5s} {'гран':>5s} {'возв':>6s} {'d6-20':>6s} {'автокорр':>9s} {'ранг':>9s} {'ошиб':>6s} | {'СТЫК':>13s} {'% цели':>7s}")
print(f"  {'ЦЕЛЬ':>6s} {'':>5s} {'':>5s} {'':>5s} {T['r1']:6.2f} {T['r2']:6.2f} {T['la']:+9.3f} {T['rc']:+9.4f} {'':>6s} | {T['j']:13.3f} {'100':>7s}")
res=[]
for pb in (0.0, 0.15, 0.30, 0.50):
    for pn in (0.15, 0.20):
        for pr in (0.10, 0.20):
            m=multi((pn,0.10,40,pr,pb))
            res.append((err(m),pn,0.10,pr,pb,m))
res.sort(key=lambda x:x[0])
for e,pn,pc,pr,pb,m in res:
    print(f"  {pn:6.2f} {pc:5.2f} {pr:5.2f} {pb:5.2f} {m['r1'][0]:6.2f} {m['r2'][0]:6.2f} "
          f"{m['la'][0]:+9.3f} {m['rc'][0]:+9.4f} {e:6.3f} | {m['j'][0]:8.3f}±{m['j'][1]:.3f} {m['j'][0]/T['j']:6.0%}")
