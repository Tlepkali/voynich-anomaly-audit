# -*- coding: utf-8 -*-
"""Какая настройка алгоритма 1 даёт табличные 57,2 % / 15,7 % / −0,33 / −16,3."""
import sys, os
sys.path=[p for p in sys.path if os.path.basename(p or ".")!="scripts"]
import json, collections, random, statistics as st, math
sys.path.insert(0,"scripts")
exec(open("scripts/decomp2.py").read().split('print("="*106)')[0])
def affixes(types,k):
    pre=collections.Counter(); suf=collections.Counter()
    for w in types:
        for L in (1,2,3):
            if len(w)>L: pre[w[:L]]+=1; suf[w[-L:]]+=1
    return [a for a,_ in pre.most_common(k)],[a for a,_ in suf.most_common(k)]
def run(lines,ntypes,k,minrem):
    words=[w for l in lines for w in l]
    types=[w for w,_ in collections.Counter(words).most_common(ntypes)] if ntypes else sorted(set(words))
    S=set(types); P,U=affixes(types,k); derived={}
    for w in sorted(S,key=len):
        for a in P:
            if w.startswith(a) and w[len(a):] in S and len(w[len(a):])>=minrem: derived[w]=w[len(a):]; break
        if w in derived: continue
        for a in U:
            if w.endswith(a) and w[:-len(a)] in S and len(w[:-len(a)])>=minrem: derived[w]=w[:-len(a)]; break
    def core(w):
        seen=set()
        while w in derived and w not in seen: seen.add(w); w=derived[w]
        return w
    root={w:core(w) for w in S}
    C=[[root.get(w,w) for w in l] for l in lines]
    T=sorted({w for l in lines for w in l}); CT=sorted({w for l in C for w in l})
    return len(derived)/len(S), shape(T),shape(CT), junc1(lines),junc1(C), slot_exc(T),slot_exc(CT)
print("="*112); print("ЦЕЛЬ ТАБЛИЦЫ §3.2:  выв. В. 57,2 %   выв. лат. 15,7 %   плотн. −0,33   стык −0,157   жёстк. −16,3"); print("="*112)
print(f"  {'типов':>7s} {'аффиксов':>8s} {'мин.остаток':>11s} | {'выв. В.':>8s} {'выв. лат.':>9s} | {'плотн.':>7s} {'стык':>8s} {'жёстк.':>8s}")
for ntypes in (5000,None):
    for k in (15,20):
        for minrem in (2,3):
            v=run(VL,ntypes,k,minrem); l=run(LL,ntypes,k,minrem)
            nm="все" if ntypes is None else str(ntypes)
            print(f"  {nm:>7s} {k:8d} {minrem:11d} | {v[0]:7.1%} {l[0]:8.1%} | {v[2]-v[1]:+7.2f} {v[4]-v[3]:+8.3f} {v[6]-v[5]:+8.2f}")

print("\n"+"="*112); print("КОНФИГУРАЦИЯ ТАБЛИЦЫ (все типы, 15 аффиксов, остаток ≥2) — значения ДО и ПОСЛЕ"); print("="*112)
for lab,L in [("Войнич",VL),("латынь",LL)]:
    r=run(L,None,15,2)
    print(f"  {lab:>8s}: выведено {r[0]:.1%} | плотность {r[1]:.2f} → {r[2]:.2f} | стык {r[3]:.3f} → {r[4]:.3f} | жёсткость {r[5]:.2f}× → {r[6]:.2f}×")
print("\n  для сравнения, конфигурация из описания §3.1 (топ-5000 типов):")
for lab,L in [("Войнич",VL),("латынь",LL)]:
    r=run(L,5000,15,2)
    print(f"  {lab:>8s}: выведено {r[0]:.1%} | плотность {r[1]:.2f} → {r[2]:.2f} | стык {r[3]:.3f} → {r[4]:.3f} | жёсткость {r[5]:.2f}× → {r[6]:.2f}×")
