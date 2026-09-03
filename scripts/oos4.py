# -*- coding: utf-8 -*-
import json, collections, random, sys, math, statistics as st, os
sys.path.insert(0,"scripts"); sys.path.insert(0,".")
exec(open("scripts/oos.py").read().split("CORP=")[0])
VOY=[w for l in VL for w in l]
def nbrs(T):
    idx=collections.defaultdict(set)
    for w in T:
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
def shape(L):
    T=set(w for l in L for w in l); nb=nbrs(T)
    def m(d):
        g=[len(nb.get(w,())) for w in T if len(w)==d]
        return st.mean(g) if len(g)>=15 else float('nan')
    return m(3),m(5),st.mean(len(nb.get(w,())) for w in T)
print("="*100); print("ФОРМА ПРОФИЛЯ ПЛОТНОСТИ: во сколько раз плотность на длине 5 меньше, чем на длине 3"); print("="*100)
print(f"  {'корпус':>18s} {'дл 3':>7s} {'дл 5':>7s} {'дл5/дл3':>9s} {'среднее':>8s}")
rows=[("Войнич (цель)",cutl(VOY))]
for nm,fn in [("латынь","latin"),("английский","english"),("немецкий","wiki_de"),("итальянский","wiki_it"),("русский","wiki_ru")]:
    p="ref/%s.clean"%fn
    if os.path.exists(p):
        L=cutl(open(p).read().split())
        if L: rows.append((nm,L))
for lab,L in rows:
    a,b,mn=shape(L)
    print(f"  {lab:>18s} {a:7.1f} {b:7.1f} {b/a:9.2f} {mn:8.2f}")
print(f"\n  {'МОДЕЛЬ, зерно':>18s}")
vals=[]
for sd in (5,11,23,37,51):
    L=model(seed=sd)
    if not L: continue
    a,b,mn=shape(L); vals.append((a,b,b/a,mn))
    print(f"  {sd:>18d} {a:7.1f} {b:7.1f} {b/a:9.2f} {mn:8.2f}")
if vals:
    print(f"  {'среднее по зёрнам':>18s} {st.mean(v[0] for v in vals):7.1f} {st.mean(v[1] for v in vals):7.1f} "
          f"{st.mean(v[2] for v in vals):9.2f} {st.mean(v[3] for v in vals):8.2f}   "
          f"(разброс дл5/дл3: {min(v[2] for v in vals):.2f}–{max(v[2] for v in vals):.2f})")
print("\n"+"="*100); print("АНАЛОГ СЕГОДНЯШНЕЙ НАХОДКИ: липнут ли РЕДКИЕ формы к непосредственному соседу"); print("="*100)
print("  (класс задаётся начальной парой знаков с частотой, ближайшей к 4 % — как у p/f в рукописи)")
def rare_adj(L, target=0.04):
    flat=[w for l in L for w in l]
    c=collections.Counter(w[:2] for w in flat); n=len(flat)
    best=min(c, key=lambda k: abs(c[k]/n-target))
    rate=c[best]/n
    mark=lambda w: w[:2]==best
    o=0; e=0.0
    for l in L:
        k=sum(1 for w in l if mark(w))
        if len(l)<2: continue
        o+=sum(1 for i in range(len(l)-1) if mark(l[i]) and mark(l[i+1]))
        e+=k*(k-1)/len(l)
    return best, rate, o, e, o/max(e,.01)
print(f"  {'корпус':>18s} {'класс':>7s} {'доля':>6s} {'набл.':>6s} {'ожид.':>7s} {'отн.':>6s}")
for lab,L in rows:
    b,r_,o,e,rt=rare_adj(L)
    print(f"  {lab:>18s} {b:>7s} {r_:5.1%} {o:6d} {e:7.1f} {rt:5.2f}×")
mv=[]
for sd in (5,11,23,37,51):
    L=model(seed=sd)
    if L:
        b,r_,o,e,rt=rare_adj(L); mv.append(rt)
        print(f"  {'МОДЕЛЬ зерно '+str(sd):>18s} {b:>7s} {r_:5.1%} {o:6d} {e:7.1f} {rt:5.2f}×")
if mv: print(f"  {'среднее модели':>18s} {'':>7s} {'':>6s} {'':>6s} {'':>7s} {st.mean(mv):5.2f}×")
print("\n  В рукописи на строках-продолжениях одноногие дают 1,30× [1,19; 1,41] (полный текст, не эта выборка).")
