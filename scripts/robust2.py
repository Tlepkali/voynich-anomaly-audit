# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, math
exec(open("scripts/robust.py").read().split('print("="*126)')[0])
def build_map(T,k=15):
    S=set(T); P,U=affixes(S,k); der={}
    for w in sorted(S,key=len):
        for a in P:
            if w.startswith(a) and w[len(a):] in S and len(w[len(a):])>=2: der[w]=w[len(a):]; break
        if w in der: continue
        for a in U:
            if w.endswith(a) and w[:-len(a)] in S and len(w[:-len(a)])>=2: der[w]=w[:-len(a)]; break
    root={}
    for w in S:
        x=w; seen=set()
        while x in der and x not in seen: seen.add(x); x=der[x]
        root[w]=x
    return root
print("="*122); print("ГЛАВНОЕ УТВЕРЖДЕНИЕ СТАТЬИ ПО ШЕСТИ ТРАНСКРИПЦИЯМ: снимается ли аномалия вместе с аффиксным слоем"); print("="*122)
print(f"  {'транскрипция':>20s} | {'плотность дл5/дл3':>26s} | {'стык по 1 знаку':>24s} | {'слотовость (типы, дл4)':>26s}")
print(f"  {'':>20s} | {'все':>8s} {'ядра':>8s} {'сдвиг':>7s} | {'все':>7s} {'ядра':>7s} {'сдвиг':>7s} | {'все':>8s} {'ядра':>8s} {'сдвиг':>7s}")
for n,lab in NAMES:
    L=load(n); T=sorted({w for l in L for w in l})
    root=build_map(T); C=[[root.get(w,w) for w in l] for l in L]
    CT=sorted({w for l in C for w in l})
    s1,s2=shape(T),shape(CT)
    j1,j2=junc1(L),junc1(C)
    m1,m2=slot_excess(T),slot_excess(CT)
    f=lambda x: f"{x:8.2f}" if x==x else "       —"
    g=lambda a,b: f"{b-a:+7.2f}" if (a==a and b==b) else "      —"
    print(f"  {lab:>20s} | {f(s1)} {f(s2)} {g(s1,s2)} | {j1:7.3f} {j2:7.3f} {j2-j1:+7.3f} | {f(m1)} {f(m2)} {g(m1,m2)}")
print("\n  ожидание: у всех трёх мер сдвиг ОТРИЦАТЕЛЬНЫЙ — аномалия уходит вместе со слоем")
