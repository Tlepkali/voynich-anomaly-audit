# -*- coding: utf-8 -*-
"""Объясняется ли плотность окрестности одной лишь позиционной структурой?
Нулевая модель: тот же алфавит, то же распределение длин, то же число типов,
знак в позиции i слова длины L берётся из наблюдённого P(знак | L, i).
"""
import json, collections, random, statistics as st, math, os
def load(n="ZL3b-n"):
    d=json.load(open(f"data/parsed_{n}.json"))
    L=[[w for w in r["words"] if '?' not in w] for r in d["rows"] if r["locus"]=="P"]
    return [l for l in L if len(l)>=3]
def nbrs(T):
    idx=collections.defaultdict(set)
    for w in T:
        idx[w].add(w)
        for i in range(len(w)): idx[w[:i]+w[i+1:]].add(w)
    nb=collections.defaultdict(set)
    for _,ws in idx.items():
        ws=list(ws)
        for i in range(len(ws)):
            for j in range(i+1,len(ws)):
                a,b=ws[i],ws[j]
                if abs(len(a)-len(b))<=1: nb[a].add(b); nb[b].add(a)
    return nb
def dens(T):
    T=set(T); nb=nbrs(T)
    m=st.mean(len(nb.get(w,())) for w in T)
    def at(d):
        g=[len(nb.get(w,())) for w in T if len(w)==d]
        return st.mean(g) if len(g)>=15 else float('nan')
    a,b=at(3),at(5)
    return m, (b/a if a==a and b==b and a>0 else float('nan'))
def posmodel(types, seed=0, cond_len=True):
    """P(знак | длина, позиция) — вся позиционная структура сохранена"""
    rnd=random.Random(seed)
    dist=collections.defaultdict(collections.Counter)
    for w in types:
        for i,c in enumerate(w):
            dist[(len(w),i) if cond_len else i][c]+=1
    pools={k:( [c for c,n in v.items() for _ in range(n)] ) for k,v in dist.items()}
    lens=[len(w) for w in types]
    out=set(); guard=0
    while len(out)<len(types) and guard<len(types)*60:
        guard+=1
        L=lens[rnd.randrange(len(lens))]
        key=lambda i:(L,i) if cond_len else i
        try: w="".join(pools[key(i)][rnd.randrange(len(pools[key(i)]))] for i in range(L))
        except KeyError: continue
        out.add(w)
    return sorted(out)
def shufmodel(types, seed=0):
    rnd=random.Random(seed); out=set()
    for w in types:
        c=list(w); rnd.shuffle(c); out.add("".join(c))
    return sorted(out)
VL=load(); LENS=[len(l) for l in VL]
TV=sorted({w for l in VL for w in l})
lw=open("ref/latin.clean").read().split(); LL=[];p=0
for n in LENS:
    if p+n>len(lw): break
    LL.append(lw[p:p+n]); p+=n
TL=sorted({w for l in LL for w in l})
print("="*104); print("ПЛОТНОСТЬ ОКРЕСТНОСТИ ПРОТИВ ПОЗИЦИОННОЙ НУЛЕВОЙ МОДЕЛИ"); print("="*104)
print(f"  {'корпус / модель':>44s} {'типов':>7s} {'соседей':>9s} {'дл5/дл3':>9s}")
for lab,T in [("ВОЙНИЧ, как есть",TV),("латынь, как есть",TL)]:
    m,s=dens(T); print(f"  {lab:>44s} {len(T):7d} {m:9.2f} {s:9.2f}")
print()
for lab,T in [("Войнич",TV),("латынь",TL)]:
    for nm,fn,ck in [("знаки перемешаны В СЛОВЕ",shufmodel,None),
                     ("P(знак | позиция)",lambda t,s: posmodel(t,s,False),None),
                     ("P(знак | ДЛИНА, позиция)",lambda t,s: posmodel(t,s,True),None)]:
        ms=[];ss=[];ns=[]
        for s_ in range(3):
            M=fn(T,s_); m,sh=dens(M); ms.append(m); ns.append(len(M))
            if sh==sh: ss.append(sh)
        print(f"  {lab+', '+nm:>44s} {int(st.mean(ns)):7d} {st.mean(ms):9.2f} "
              f"{(st.mean(ss) if ss else float('nan')):9.2f}")
    print()
