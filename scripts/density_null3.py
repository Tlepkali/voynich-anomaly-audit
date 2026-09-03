# -*- coding: utf-8 -*-
"""Не запоминает ли марковская модель сам словарь? И держится ли результат
на других транскрипциях."""
import json, collections, random, statistics as st, math
exec(open("scripts/density_null2.py").read().split('print("="*100)')[0])
print("="*100); print("НЕ ЗАПОМИНАЕТ ЛИ МОДЕЛЬ СЛОВАРЬ: доля порождённых слов, которые ЕСТЬ в оригинале"); print("="*100)
print(f"  {'корпус':>10s} {'порядок':>8s} {'совпало с оригиналом':>21s} {'соседей':>9s} {'соседей на НОВЫХ':>18s}")
for lab,T in [("ВОЙНИЧ",TV),("латынь",TL)]:
    S=set(T)
    for o in (1,2,3):
        ov=[];dn=[];dnew=[]
        for sd in range(3):
            M=markov(T,o,sd)
            if len(M)<len(T)*0.5: continue
            inter=len(set(M)&S)/len(M); ov.append(inter)
            dn.append(dens(M)[0])
            new=[w for w in M if w not in S]
            if len(new)>500:
                nb=nbrs(set(M))
                dnew.append(st.mean(len(nb.get(w,())) for w in new))
        if not ov: continue
        print(f"  {lab:>10s} {o:8d} {st.mean(ov):20.1%} {st.mean(dn):9.2f} "
              f"{(st.mean(dnew) if dnew else float('nan')):18.2f}")
    print()
print("="*100); print("ТО ЖЕ НА ДРУГИХ ТРАНСКРИПЦИЯХ (марков порядка 2 — где запоминание мало)"); print("="*100)
print(f"  {'транскрипция':>16s} {'наблюдено':>10s} {'марков-2':>9s} {'отношение':>10s} {'совпало':>9s}")
for n,lab in [("ZL3b-n","Зандб.–Ландини"),("IT2a-n","Такахаси"),("RF1b-e","RF1b-e"),("GC2a-n","Класton v101")]:
    L=load(n); T=sorted({w for l in L for w in l}); S=set(T)
    m0=dens(T)[0]; ms=[];ov=[]
    for sd in range(2):
        M=markov(T,2,sd)
        if len(M)<len(T)*0.5: continue
        ms.append(dens(M)[0]); ov.append(len(set(M)&S)/len(M))
    if not ms: continue
    print(f"  {lab:>16s} {m0:10.2f} {st.mean(ms):9.2f} {m0/st.mean(ms):9.2f}× {st.mean(ov):8.1%}")
