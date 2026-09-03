# -*- coding: utf-8 -*-
"""Более жёсткая нулевая модель: марковская цепь по знакам внутри слова
(порядок 1, 2 и 3), обученная на самом корпусе. То же число типов, то же
распределение длин. Если плотность — следствие локальной статистики знаков,
такая модель её воспроизведёт."""
import json, collections, random, statistics as st, math
exec(open("scripts/density_null.py").read().split('VL=load()')[0])
VL=load(); LENS=[len(l) for l in VL]
TV=sorted({w for l in VL for w in l})
lw=open("ref/latin.clean").read().split(); LL=[];p=0
for n in LENS:
    if p+n>len(lw): break
    LL.append(lw[p:p+n]); p+=n
TL=sorted({w for l in LL for w in l})
def markov(types, order, seed=0):
    rnd=random.Random(seed)
    tr=collections.defaultdict(collections.Counter)
    for w in types:
        s="^"*order+w+"$"
        for i in range(order, len(s)): tr[s[i-order:i]][s[i]]+=1
    pools={k:[c for c,n in v.items() for _ in range(n)] for k,v in tr.items()}
    lens=collections.Counter(len(w) for w in types)
    want=collections.Counter({k:v for k,v in lens.items()})
    out=set(); guard=0; got=collections.Counter()
    while len(out)<len(types) and guard<len(types)*200:
        guard+=1
        ctx="^"*order; w=""
        while True:
            p_=pools.get(ctx)
            if not p_: break
            c=p_[rnd.randrange(len(p_))]
            if c=="$": break
            w+=c; ctx=(ctx+c)[-order:]
            if len(w)>25: break
        if not w: continue
        if got[len(w)]>=want.get(len(w),0): continue     # держим распределение длин
        if w in out: continue
        out.add(w); got[len(w)]+=1
    return sorted(out)
print("="*100); print("МАРКОВСКИЕ НУЛЕВЫЕ МОДЕЛИ ПО ЗНАКАМ (обучены на самом корпусе)"); print("="*100)
print(f"  {'корпус / модель':>40s} {'типов':>7s} {'соседей':>9s} {'дл5/дл3':>9s} {'к наблюд.':>10s}")
for lab,T in [("ВОЙНИЧ",TV),("латынь",TL)]:
    m0,s0=dens(T)
    print(f"  {lab+', как есть':>40s} {len(T):7d} {m0:9.2f} {s0:9.2f} {'—':>10s}")
    for o in (1,2,3):
        ms=[];ss=[];ns=[]
        for sd in range(3):
            M=markov(T,o,sd)
            if len(M)<len(T)*0.5: continue
            m,sh=dens(M); ms.append(m); ns.append(len(M))
            if sh==sh: ss.append(sh)
        if not ms: print(f"  {lab+f', марков порядка {o}':>40s}  — не набралось типов"); continue
        print(f"  {lab+f', марков порядка {o}':>40s} {int(st.mean(ns)):7d} {st.mean(ms):9.2f} "
              f"{(st.mean(ss) if ss else float('nan')):9.2f} {m0/max(st.mean(ms),1e-9):9.2f}×")
    print()
