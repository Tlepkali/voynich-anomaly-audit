# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, math, os
exec(open("scripts/regen.py").read().split('print("="*104)')[0])
print("="*100); print("БАЗА И ДЛИНЫ"); print("="*100)
print(f"  {'корпус':>16s} {'типов':>7s} {'ср.длина типов':>15s} {'доля порождения':>16s}")
CORP=[("ВОЙНИЧ",TV)]
for fn,lab in [("latin.clean","латынь"),("bk_es.clean","испанский"),("bk_it.clean","итальянский")]:
    if os.path.exists("ref/"+fn): CORP.append((lab, sorted(set(open(f"ref/{fn}",encoding='utf-8',errors='ignore').read().split()))))
for lab,T in CORP:
    v=[regen(T,2,s)[0] for s in range(3)]
    print(f"  {lab:>16s} {len(T):7d} {st.mean(len(w) for w in T):15.2f} {st.mean(v):15.1%}")
print("\n"+"="*100); print("ВЫРАВНИВАНИЕ ПО ДЛИНЕ В ДРУГУЮ СТОРОНУ: берём у рукописи только ДЛИННЫЕ типы"); print("="*100)
print("  (у латыни мало коротких слов, поэтому подтягиваем не её вниз, а рукопись вверх)")
print(f"  {'выборка':>34s} {'типов':>7s} {'ср.длина':>9s} {'доля':>8s}")
for lo in (0,6,7,8):
    sub=[w for w in TV if len(w)>=lo] if lo else TV
    if len(sub)<1500: continue
    rnd=random.Random(5); sub=sorted(rnd.sample(sub,min(len(sub),len(sub))))
    v=[regen(sub,2,s)[0] for s in range(3)]
    lab=f"Войнич, длина ≥ {lo}" if lo else "Войнич, все типы"
    print(f"  {lab:>34s} {len(sub):7d} {st.mean(len(w) for w in sub):9.2f} {st.mean(v):7.1%}")
for fn,lab in [("latin.clean","латынь"),("bk_es.clean","испанский")]:
    if not os.path.exists("ref/"+fn): continue
    T=sorted(set(open(f"ref/{fn}",encoding='utf-8',errors='ignore').read().split()))
    for lo in (7,8):
        sub=[w for w in T if len(w)>=lo]
        if len(sub)<1500: continue
        v=[regen(sub,2,s)[0] for s in range(3)]
        print(f"  {lab+f', длина ≥ {lo}':>34s} {len(sub):7d} {st.mean(len(w) for w in sub):9.2f} {st.mean(v):7.1%}")
print("\n"+"="*100); print("ПРИ ПАРНОМ ВЫРАВНИВАНИИ И ПО ЧИСЛУ ТИПОВ, И ПО СРЕДНЕЙ ДЛИНЕ"); print("="*100)
def pair(T, n, target_mean, seed=0, tol=0.25):
    rnd=random.Random(seed); best=None
    for _ in range(400):
        s=rnd.sample(T, min(n,len(T)))
        m=st.mean(len(w) for w in s)
        if abs(m-target_mean)<tol: return sorted(s)
        if best is None or abs(m-target_mean)<best[0]: best=(abs(m-target_mean), s)
    return sorted(best[1])
mV=st.mean(len(w) for w in TV)
print(f"  цель: {len(TV)} типов, средняя длина {mV:.2f}\n")
print(f"  {'корпус':>16s} {'типов':>7s} {'ср.длина':>9s} {'доля':>8s} {'к Войничу':>11s}")
vv=st.mean(regen(TV,2,s)[0] for s in range(3))
print(f"  {'ВОЙНИЧ':>16s} {len(TV):7d} {mV:9.2f} {vv:7.1%} {'—':>11s}")
for lab,T in CORP[1:]:
    long_ok=[w for w in T if len(w)<=int(mV)+3]
    M=pair(long_ok, len(TV), mV)
    v=[regen(M,2,s)[0] for s in range(3)]
    print(f"  {lab:>16s} {len(M):7d} {st.mean(len(w) for w in M):9.2f} {st.mean(v):7.1%} {vv/max(st.mean(v),1e-9):10.1f}×")
