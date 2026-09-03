# -*- coding: utf-8 -*-
"""Гибрид: слово СТРОИТСЯ по знакам с ограничением на границе (стык даром),
а словесные памяти навешиваются сверху. Конкурируют ли они теперь между собой,
раз граница бюджета не тратит?
ПОДГОНКА по возврату, автокорреляции и ранг-корреляции; СТЫК ОТЛОЖЕН."""
import json, collections, random, statistics as st, math
exec(open("scripts/construct.py").read().split('print("="*104)')[0])
TYPES=sorted(set(VOY))
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
NB=nbr_map(TYPES)
c=collections.Counter(VOY); order_=[w for w,_ in c.most_common()]
step=max(1,len(order_)//6); CLS={w:min(i//step,5) for i,w in enumerate(order_)}
BYCLS=collections.defaultdict(list)
for w in VOY: BYCLS[CLS[w]].append(w)
MODEL=build_model(2,"tokens")
def hybrid(pn,pc,pr,seed=0,wc=40,maxlen=25):
    pools,bpool,fpool,o=MODEL
    rnd=random.Random(seed); out=[]; prev=None; q=collections.deque(maxlen=wc)
    while len(out)<len(VOY):
        u=rnd.random(); x=None
        if prev is not None and u<pn and NB.get(prev):
            n=NB[prev]; x=n[rnd.randrange(len(n))]
        elif q and u<pn+pc: x=q[rnd.randrange(len(q))]
        elif prev is not None and u<pn+pc+pr:
            b=BYCLS[CLS.get(prev,0)]
            if b: x=b[rnd.randrange(len(b))]
        if x is None:                       # СТРОИМ, с ограничением на границе
            if prev is not None and bpool.get(prev[-1]):
                p=bpool[prev[-1]]; c0=p[rnd.randrange(len(p))]
            else: c0=fpool[rnd.randrange(len(fpool))]
            x=c0; ctx=("^"*o+c0)[-o:]
            while True:
                p=pools.get(ctx)
                if not p: break
                ch=p[rnd.randrange(len(p))]
                if ch=="$": break
                x+=ch; ctx=(ctx+ch)[-o:]
                if len(x)>=maxlen: break
        out.append(x); prev=x; q.append(x)
    return cut(out[:len(VOY)])
def multi(args,seeds=3):
    ds=[battery(hybrid(*args,seed=s),"") for s in range(seeds)]
    return {k:(st.mean(d[k] for d in ds), st.stdev(d[k] for d in ds) if len(ds)>1 else 0) for k in ("r1","r2","la","rc","j")}
def err(m):
    return (abs(m['r1'][0]-T['r1'])/T['r1']+abs(m['r2'][0]-T['r2'])/T['r2']
            +abs(m['la'][0]-T['la'])/abs(T['la'])+abs(m['rc'][0]-T['rc'])/abs(T['rc']))
print("="*110); print("ГИБРИД: построение даёт стык, словесные памяти навешены сверху"); print("="*110)
print(f"  {'сосед':>6s} {'кеш':>5s} {'част':>5s} | {'возврат':>8s} {'d6-20':>7s} {'автокорр':>10s} {'ранг':>10s} {'ошиб':>6s} | {'СТЫК отложен':>14s}")
print(f"  {'ЦЕЛЬ':>6s} {'':>5s} {'':>5s} | {T['r1']:8.2f} {T['r2']:7.2f} {T['la']:+10.3f} {T['rc']:+10.4f} {'':>6s} | {T['j']:9.3f} 100%")
res=[]
for pn in (0.10,0.15,0.20,0.25):
    for pc in (0.05,0.10,0.15):
        for pr in (0.0,0.10):
            m=multi((pn,pc,pr)); res.append((err(m),pn,pc,pr,m))
res.sort(key=lambda x:x[0])
for e,pn,pc,pr,m in res[:8]:
    print(f"  {pn:6.2f} {pc:5.2f} {pr:5.2f} | {m['r1'][0]:8.2f} {m['r2'][0]:7.2f} {m['la'][0]:+10.3f} "
          f"{m['rc'][0]:+10.4f} {e:6.3f} | {m['j'][0]:9.3f} {m['j'][0]/T['j']:4.0%}")
