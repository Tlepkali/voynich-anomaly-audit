# -*- coding: utf-8 -*-
"""Порождение ПОСТРОЕНИЕМ, а не выбором: слово собирается по знакам, первый знак
берётся из распределения, наблюдённого после последнего знака предыдущего слова.
Бюджета выбора нет вовсе — выбирать не из чего.
УСЛОВИЯ: ни один параметр не подгоняется ни под одну из четырёх подписей.
Все четыре отложены."""
import json, collections, random, statistics as st, math
exec(open("scripts/memory.py").read().split('print("="*112)')[0])
T=battery(VL,"РУКОПИСЬ")
def build_model(order=2, on="tokens"):
    src = VOY if on=="tokens" else sorted(set(VOY))
    tr=collections.defaultdict(collections.Counter)
    for w in src:
        s="^"*order+w+"$"
        for i in range(order,len(s)): tr[s[i-order:i]][s[i]]+=1
    pools={k:[c for c,n in v.items() for _ in range(n)] for k,v in tr.items()}
    # граница: какой первый знак идёт после какого последнего
    bnd=collections.defaultdict(collections.Counter)
    for l in VL:
        for a,b in zip(l,l[1:]): bnd[a[-1]][b[0]]+=1
    bpool={k:[c for c,n in v.items() for _ in range(n)] for k,v in bnd.items()}
    first=collections.Counter(w[0] for w in src)
    fpool=[c for c,n in first.items() for _ in range(n)]
    return pools, bpool, fpool, order
def generate(model, use_boundary=True, seed=0, maxlen=25):
    pools,bpool,fpool,order=model
    rnd=random.Random(seed); out=[]; prev=None
    total=len(VOY)
    while len(out)<total:
        if use_boundary and prev is not None and bpool.get(prev[-1]):
            p=bpool[prev[-1]]; c0=p[rnd.randrange(len(p))]
        else:
            c0=fpool[rnd.randrange(len(fpool))]
        w=c0; ctx=("^"*order+c0)[-order:]
        while True:
            p=pools.get(ctx)
            if not p: break
            c=p[rnd.randrange(len(p))]
            if c=="$": break
            w+=c; ctx=(ctx+c)[-order:]
            if len(w)>=maxlen: break
        out.append(w); prev=w
    return cut(out[:total])
def show(rows):
    print(f"  {'модель':>34s} {'возврат d1-5':>13s} {'d6-20':>8s} {'автокорр':>10s} {'ранг':>10s} {'СТЫК':>8s}")
    print(f"  {'ЦЕЛЬ':>34s} {T['r1']:13.2f} {T['r2']:8.2f} {T['la']:+10.3f} {T['rc']:+10.4f} {T['j']:8.3f}")
    for lab,ds in rows:
        m={k:(st.mean(d[k] for d in ds), st.stdev(d[k] for d in ds) if len(ds)>1 else 0) for k in ("r1","r2","la","rc","j")}
        print(f"  {lab:>34s} {m['r1'][0]:13.2f} {m['r2'][0]:8.2f} {m['la'][0]:+10.3f} {m['rc'][0]:+10.4f} {m['j'][0]:8.3f}")
        print(f"  {'(доля цели)':>34s} {m['r1'][0]/T['r1']:12.0%} {m['r2'][0]/T['r2']:7.0%} {m['la'][0]/T['la']:9.0%} {m['rc'][0]/T['rc']:9.0%} {m['j'][0]/T['j']:7.0%}")
print("="*104); print("ПОСТРОЕНИЕ ВМЕСТО ВЫБОРА: слово собирается по знакам"); print("="*104)
rows=[]
for on in ("tokens","types"):
    for o in (2,3):
        M=build_model(o,on)
        ds=[four_or_battery for four_or_battery in []]
        ds=[battery(generate(M,True,s),"") for s in range(3)]
        rows.append((f"цепь порядка {o} на {on}, граница ДА", ds))
        ds0=[battery(generate(M,False,s),"") for s in range(3)]
        rows.append((f"цепь порядка {o} на {on}, границы нет", ds0))
show(rows)
