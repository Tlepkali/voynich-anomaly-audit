# -*- coding: utf-8 -*-
import json, collections, random, sys, math, statistics as st
sys.path.insert(0,"scripts"); sys.path.insert(0,".")
exec(open("scripts/oos.py").read().split("CORP=")[0])   # берём модель как есть, без её печати
VOY=[w for l in VL for w in l]
def cut(u):
    out=[];k=0
    for n in LENS:
        if k+n>len(u): return out
        out.append(u[k:k+n]); k+=n
    return out
CORP={"Войнич (цель)":cutl(VOY), "МОДЕЛЬ":model()}
for nm,fn in [("латынь","latin"),("английский","english"),("немецкий","german")]:
    try:
        w=open("ref/%s.clean"%fn).read().split(); L=cutl(w)
        if L: CORP[nm]=L
    except FileNotFoundError: pass
print("корпуса:", {k:sum(len(l) for l in v) for k,v in CORP.items()})
def nbrs(types):
    idx=collections.defaultdict(set)
    for w in types:
        idx[w].add(w)
        for i in range(len(w)): idx[w[:i]+w[i+1:]].add(w)
    nb=collections.defaultdict(set)
    for k,ws in idx.items():
        ws=list(ws)
        for i in range(len(ws)):
            for j in range(i+1,len(ws)):
                a,b=ws[i],ws[j]
                if abs(len(a)-len(b))<=1: nb[a].add(b); nb[b].add(a)
    return nb
print("\n"+"="*112); print("1. ПЛОТНОСТЬ ОКРЕСТНОСТИ (соседей на расстоянии 1, по типам) — НЕ УЧАСТВОВАЛА В НАСТРОЙКЕ"); print("="*112)
print(f"  {'корпус':>16s} {'типов':>7s} {'соседей':>8s} | "+" ".join(f"{'дл '+str(d):>7s}" for d in range(3,9)))
DENS={}
for lab,L in CORP.items():
    T=set(w for l in L for w in l); nb=nbrs(T)
    mean=st.mean(len(nb.get(w,())) for w in T); DENS[lab]=mean
    row=[]
    for d in range(3,9):
        g=[len(nb.get(w,())) for w in T if len(w)==d]
        row.append(st.mean(g) if len(g)>=15 else float('nan'))
    print(f"  {lab:>16s} {len(T):7,d} {mean:8.2f} | "+" ".join(f"{x:7.1f}" if x==x else "      —" for x in row))
print("\n"+"="*112); print("2. СОСЕДСТВО ПОХОЖИХ ТОКЕНОВ (против перемешивания ВНУТРИ строки)"); print("="*112)
def near(a,b):
    if a==b: return True
    la,lb=len(a),len(b)
    if abs(la-lb)>1: return False
    if la==lb:
        d=0
        for x,y in zip(a,b):
            if x!=y:
                d+=1
                if d>1: return False
        return d==1
    s_,l_=(a,b) if la<lb else (b,a)
    return any(l_[:i]+l_[i+1:]==s_ for i in range(len(l_)))
def ratio(L,pred,B=8,seed=3):
    o=sum(1 for l in L for i in range(len(l)-1) if pred(l[i],l[i+1]))
    rnd=random.Random(seed); acc=0.0
    for _ in range(B):
        for l in L:
            p=rnd.sample(l,len(l)); acc+=sum(1 for a,b in zip(p,p[1:]) if pred(a,b))/B
    return o/max(acc,.01)
print(f"  {'корпус':>16s} {'одинаковые (НАСТРАИВАЛОСЬ)':>28s} {'почти-одинаковые (НЕТ)':>26s}")
for lab,L in CORP.items():
    print(f"  {lab:>16s} {ratio(L,lambda a,b:a==b):27.2f}× {ratio(L,near):25.2f}×")
