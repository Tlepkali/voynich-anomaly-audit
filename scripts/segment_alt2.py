# -*- coding: utf-8 -*-
"""Случайная ре-сегментация в той же доле: держатся ли меры вообще, или только
при склейке именно тех пробелов, что помечены транскриптором."""
import collections, random, statistics as st, math
exec(open("scripts/segment_alt.py").read().split('print("="*104)')[0])
BASE=parse('.')
def rejoin(L, p, seed):
    rnd=random.Random(seed); out=[]
    for l in L:
        row=[l[0]]
        for w in l[1:]:
            if rnd.random()<p: row[-1]=row[-1]+w
            else: row.append(w)
        out.append(row)
    return [l for l in out if len(l)>=3]
def battery(L):
    T=sorted({w for l in L for w in l}); f=[w for l in L for w in l]
    m,sh=dens(T); M=markov(T,2,None,0)
    return dict(n=len(f),ty=len(T),rc=rank_corr(L),adj=adj(L),dens=m,shape=sh,
                j=junc1(L),slot=slot_exc(T),regen=len(set(M)&set(T))/max(len(M),1))
print("="*104); print("СЛУЧАЙНАЯ СКЛЕЙКА В ТОЙ ЖЕ ДОЛЕ (18,4 %), три посева"); print("="*104)
b0=battery(BASE)
runs=[battery(rejoin(BASE,0.184,s)) for s in range(3)]
alt=battery(parse(''))
print(f"  {'мера':>26s} {'исходная':>10s} {'по транскр.':>12s} {'случайная':>12s} {'разброс':>16s}")
def line(nm,k,fmt="%.3f",pct=False):
    f=lambda x:(f"{x:.1%}" if pct else fmt%x) if x==x else "—"
    v=[r[k] for r in runs if r[k]==r[k]]
    print(f"  {nm:>26s} {f(b0[k]):>10s} {f(alt[k]):>12s} {f(st.mean(v)):>12s} "
          f"{('['+f(min(v))+'; '+f(max(v))+']'):>16s}")
line("токенов","n","%d"); line("типов","ty","%d")
line("ранг-корреляция","rc","%+.4f")
line("соседство одинаковых","adj","%.2f")
line("плотность","dens","%.2f")
line("форма дл5/дл3","shape","%.2f")
line("стык по 1 знаку","j","%.3f")
line("слотовость","slot","%.2f")
line("порождение цепью","regen",pct=True)
print("\n  для сравнения — те же меры у ЛАТЫНИ (исходная сегментация):")
print("  плотность 1,65 | форма 0,41 | стык 0,047 | слотовость 8,59 | порождение 1,5–2,3 % | ранг-корр −0,088")
