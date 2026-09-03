# -*- coding: utf-8 -*-
"""Четвёртая архитектура: память ПОДЧИНЕНА границе.
Всякий кандидат из памяти — сосед, кеш, класс частоты — фильтруется по тому,
законен ли его первый знак после последнего знака предыдущего слова. Если
подходящих нет, слово СТРОИТСЯ. Стык держится всегда, разбавлять его нечем.
ПОДГОНКА по возврату, автокорреляции и ранг-корреляции; СТЫК ОТЛОЖЕН."""
import json, collections, random, statistics as st, math
exec(open("scripts/construct2.py").read().split('def multi(')[0])
POOLS,BPOOL,FPOOL,ORD=MODEL
BSET={k:set(v) for k,v in BPOOL.items()}       # какие первые знаки законны после k
BYINIT=collections.defaultdict(list)
for w in TYPES: BYINIT[w[0]].append(w)
def legal(prev):
    return BSET.get(prev[-1]) if prev is not None else None
def pick(cands, ok, rnd):
    """кандидаты, чей первый знак законен после предыдущего"""
    if ok is None: 
        return cands[rnd.randrange(len(cands))] if cands else None
    f=[w for w in cands if w[0] in ok]
    return f[rnd.randrange(len(f))] if f else None
def build_word(prev, rnd, maxlen=25):
    ok=legal(prev)
    if prev is not None and BPOOL.get(prev[-1]):
        p=BPOOL[prev[-1]]; c0=p[rnd.randrange(len(p))]
    else: c0=FPOOL[rnd.randrange(len(FPOOL))]
    w=c0; ctx=("^"*ORD+c0)[-ORD:]
    while True:
        p=POOLS.get(ctx)
        if not p: break
        ch=p[rnd.randrange(len(p))]
        if ch=="$": break
        w+=ch; ctx=(ctx+ch)[-ORD:]
        if len(w)>=maxlen: break
    return w
def arch4(pn,pc,pr,seed=0,wc=40):
    rnd=random.Random(seed); out=[]; prev=None; q=collections.deque(maxlen=wc)
    while len(out)<len(VOY):
        ok=legal(prev); u=rnd.random(); x=None
        if prev is not None and u<pn and NB.get(prev):
            x=pick(NB[prev], ok, rnd)
        elif q and u<pn+pc:
            x=pick(list(q), ok, rnd)
        elif prev is not None and u<pn+pc+pr:
            x=pick(BYCLS.get(CLS.get(prev,0),[]), ok, rnd)
        if x is None: x=build_word(prev, rnd)      # не нашлось законного — строим
        out.append(x); prev=x; q.append(x)
    return cut(out[:len(VOY)])
def multi(args,seeds=3):
    ds=[battery(arch4(*args,seed=s),"") for s in range(seeds)]
    return {k:(st.mean(d[k] for d in ds), st.stdev(d[k] for d in ds) if len(ds)>1 else 0) for k in ("r1","r2","la","rc","j")}
def err(m):
    return (abs(m['r1'][0]-T['r1'])/T['r1']+abs(m['r2'][0]-T['r2'])/T['r2']
            +abs(m['la'][0]-T['la'])/abs(T['la'])+abs(m['rc'][0]-T['rc'])/abs(T['rc']))
print("="*112); print("ЧЕТВЁРТАЯ АРХИТЕКТУРА: память подчинена границе"); print("="*112)
print(f"  {'сосед':>6s} {'кеш':>5s} {'част':>5s} | {'возврат':>10s} {'d6-20':>8s} {'автокорр':>11s} {'ранг':>11s} {'ошиб':>6s} | {'СТЫК отложен':>15s}")
print(f"  {'ЦЕЛЬ':>6s} {'':>5s} {'':>5s} | {T['r1']:10.2f} {T['r2']:8.2f} {T['la']:+11.3f} {T['rc']:+11.4f} {'':>6s} | {T['j']:10.3f} 100%")
res=[]
for pn in (0.15,0.25,0.35):
    for pc in (0.05,0.10,0.20):
        for pr in (0.0,0.10,0.20):
            m=multi((pn,pc,pr)); res.append((err(m),pn,pc,pr,m))
res.sort(key=lambda x:x[0])
for e,pn,pc,pr,m in res[:8]:
    f=lambda k: m[k][0]/T[k]
    print(f"  {pn:6.2f} {pc:5.2f} {pr:5.2f} | {m['r1'][0]:7.2f}/{f('r1'):3.0%} {m['r2'][0]:8.2f} "
          f"{m['la'][0]:+8.3f}/{f('la'):3.0%} {m['rc'][0]:+8.4f}/{f('rc'):3.0%} {e:6.3f} | {m['j'][0]:10.3f} {f('j'):4.0%}")
print("\n  порог «взято» = 70 % цели; смотрим, есть ли точка со всеми четырьмя")
best=[(e,p,m) for e,pn,pc,pr,m in res for p in [(pn,pc,pr)]
      if all(m[k][0]/T[k]>=0.70 for k in ("r1","la","rc","j"))]
print(f"  точек, взявших ВСЕ ЧЕТЫРЕ: {len(best)}")
for e,p,m in best[:3]:
    print(f"    сосед {p[0]}, кеш {p[1]}, частота {p[2]}: "+", ".join(f"{k} {m[k][0]/T[k]:.0%}" for k in ("r1","la","rc","j")))
