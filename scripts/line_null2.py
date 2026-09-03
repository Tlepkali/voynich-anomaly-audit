# -*- coding: utf-8 -*-
"""ПРАВИЛЬНЫЙ НУЛЬ к «остатку начала строки».

Я объявил находку: остаток начального слова отличается от остатка серединного
на 0,27 при нуле 0,05, p=0,005, на шести транскрипциях. Нуль был ПЕРЕМЕШИВАНИЕ
ВНУТРИ СТРАНИЦЫ — оно разрушает и приписывание тоже, поэтому и давало 0,05.
Вопрос был не «есть ли строчная структура», а «есть ли что-то СВЕРХ
приписывания», и нуль обязан был содержать приписывание.

Здесь нуль такой: генератор, который ТОЛЬКО приписывает знак, с долей,
ПОДОГНАННОЙ ПО ДЛИНЕ (единственная подгонка). Расхождение остатков отложено.
"""
import json, collections, random, statistics as st, math, sys
exec(open("scripts/arch_line.py").read().split('V=dict(ldiv=')[0])
VT_MS=set(VOY)

def stem_div(L):
    T={w for l in L for w in l}
    FI=[l[0] for l in L if l]; MID=[w for l in L for w in l[1:]]
    a=collections.Counter(w[1] for w in FI if len(w)>2 and w[1:] in T)
    b=collections.Counter(w[1] for w in MID if len(w)>2 and w[1:] in T)
    ta,tb=sum(a.values()),sum(b.values())
    if ta<100 or tb<100: return float("nan")
    return sum(abs(a[c]/ta-b[c]/tb) for c in set(a)|set(b))/2, a, b
def lendiff(L):
    FI=[l[0] for l in L if l]; MID=[w for l in L for w in l[1:]]
    return st.mean(len(w) for w in FI)-st.mean(len(w) for w in MID)

obs_sd,A,B=stem_div(VL); obs_ld=lendiff(VL)
print("="*96); print("КАЛИБРОВКА ГЕНЕРАТОРА ПО ОДНОЙ ЛИШЬ ДЛИНЕ"); print("="*96)
print(f"  рукопись: разница длин {obs_ld:+.3f}, расхождение остатков {obs_sd:.3f} (ОТЛОЖЕНО)")
print(f"\n  {'p':>5s} {'разница длин':>13s} {'расхожд. остатков':>18s}")
cand={}
for p in [0.2,0.3,0.4,0.5,0.6]:
    Ls=[gen_lines(p,seed=s) for s in range(3)]
    ld=st.mean(lendiff(L) for L in Ls); sd=st.mean(stem_div(L)[0] for L in Ls)
    cand[p]=(ld,sd); print(f"  {p:5.2f} {ld:+13.3f} {sd:18.3f}")
pstar=min(cand, key=lambda p: abs(cand[p][0]-obs_ld))
print(f"\n  подогнано ПО ДЛИНЕ: p* = {pstar}  (разница длин {cand[pstar][0]:+.3f} против {obs_ld:+.3f})")

print("\n"+"="*96); print("ОТЛОЖЕННАЯ МЕРА ПРИ ЭТОМ p*, 20 ЗЁРЕН"); print("="*96)
vals=[stem_div(gen_lines(pstar,seed=s))[0] for s in range(20)]
lo,hi=min(vals),max(vals)
print(f"  генератор, ТОЛЬКО приписывание: {st.mean(vals):.3f} [{lo:.3f}; {hi:.3f}]")
print(f"  рукопись:                       {obs_sd:.3f}")
inside = lo<=obs_sd<=hi
print(f"\n  наблюдённое {'ВНУТРИ' if inside else 'ВНЕ'} разброса нуля → "
      f"{'находка СНИМАЕТСЯ: приписывания достаточно' if inside else 'остаток есть'}")

print("\n"+"="*96); print("И ХАРАКТЕРИСТИКА: даёт ли приписывание те же знаки"); print("="*96)
G=gen_lines(pstar,seed=0); _,ga,gb=stem_div(G)
ta,tb=sum(A.values()),sum(B.values()); ga_t,gb_t=sum(ga.values()),sum(gb.values())
print(f"  {'знак':>5s} {'рукопись нач.':>14s} {'рукопись сер.':>14s} {'генер. нач.':>12s} {'генер. сер.':>12s}")
for c in sorted(set(A)|set(B), key=lambda c: -(A[c]/ta)):
    if A[c]/ta<0.03 and B[c]/tb<0.03: continue
    print(f"  {c:>5s} {A[c]/ta:13.1%} {B[c]/tb:13.1%} {ga[c]/ga_t:11.1%} {gb[c]/gb_t:11.1%}")
