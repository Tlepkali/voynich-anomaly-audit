# -*- coding: utf-8 -*-
"""Настоящая ли находка «цепь порождает 28,8 % словаря», или это следствие
меньшего и более короткого словаря. Выравниваем по числу типов и по длинам."""
import json, collections, random, statistics as st, math, os
exec(open("scripts/density_null2.py").read().split('print("="*100)')[0])
def match_lengths(types, target_lens, n_types, seed=0):
    """подсловарь с тем же распределением длин и тем же числом типов"""
    rnd=random.Random(seed)
    byl=collections.defaultdict(list)
    for w in types: byl[len(w)].append(w)
    for k in byl: rnd.shuffle(byl[k])
    want=collections.Counter(target_lens)
    scale=n_types/max(sum(want.values()),1)
    out=[]
    for L,c in want.items():
        need=int(round(c*scale)); pool=byl.get(L,[])
        out+=pool[:need]
    return sorted(set(out))
def regen(types, order=2, seed=0):
    M=markov(types, order, seed)
    if not M: return float('nan'), 0
    return len(set(M)&set(types))/len(M), len(M)
def load_types(fn, lines=None):
    if fn.endswith(".clean"):
        w=open(f"ref/{fn}",encoding="utf-8",errors="ignore").read().split()
        return sorted(set(w))
    return None
VL=load(); LENS=[len(l) for l in VL]
TV=sorted({w for l in VL for w in l})
VLENS=[len(w) for w in TV]
print("="*104); print("ДОЛЯ ПОРОЖДЁННЫХ СЛОВ, СОВПАВШИХ С ОРИГИНАЛОМ (цепь 2-го порядка)"); print("="*104)
print(f"  {'корпус':>34s} {'типов':>7s} {'ср.длина':>9s} {'доля':>8s}")
rows=[("ВОЙНИЧ, как есть", TV)]
for fn,lab in [("latin.clean","латынь"),("bk_es.clean","испанский"),("bk_it.clean","итальянский"),("english.clean","английский")]:
    if os.path.exists("ref/"+fn):
        T=load_types(fn); rows.append((lab+", как есть", T))
for lab,T in rows:
    v=[regen(T,2,s)[0] for s in range(3)]
    print(f"  {lab:>34s} {len(T):7d} {st.mean(len(w) for w in T):9.2f} {st.mean(v):7.1%}")
print("\n  ВЫРОВНЕНО по числу типов рукописи (7 205) И по её распределению длин:")
for lab,T in rows[1:]:
    M=match_lengths(T, VLENS, len(TV))
    if len(M)<3000: print(f"  {lab.split(',')[0]+', выровнен':>34s}  — не набралось ({len(M)} типов)"); continue
    v=[regen(M,2,s)[0] for s in range(3)]
    print(f"  {lab.split(',')[0]+', выровнен':>34s} {len(M):7d} {st.mean(len(w) for w in M):9.2f} {st.mean(v):7.1%}")
print("\n"+"="*104); print("НЕ РАСТЁТ ЛИ ДОЛЯ МЕХАНИЧЕСКИ ПРИ СЖАТИИ СЛОВАРЯ"); print("="*104)
print(f"  {'корпус':>16s} "+" ".join(f"{str(n)+' типов':>12s}" for n in (2000,4000,7205,11000)))
for lab,T in [("ВОЙНИЧ",TV)]+[(l.split(',')[0],t) for l,t in rows[1:]]:
    cells=[]
    for n in (2000,4000,7205,11000):
        if len(T)<n: cells.append("          —"); continue
        rnd=random.Random(9); sub=sorted(rnd.sample(T,n))
        v=[regen(sub,2,s)[0] for s in range(2)]
        cells.append(f"{st.mean(v):11.1%}")
    print(f"  {lab:>16s} "+" ".join(cells))
