# -*- coding: utf-8 -*-
"""Два утверждения Шиннера 2007 (Cryptologia, «Evidence of the Hoax Hypothesis»),
цитируемые Редди-Найтом и Зандбергеном:
  1. знаки показывают дальние корреляции на расстояниях СВЫШЕ 72 знаков,
     что «чуть больше средней длины строки»;
  2. вероятность повтора ПОХОЖИХ слов на данном расстоянии подчиняется
     ГЕОМЕТРИЧЕСКОМУ распределению.
Оба проверяемы прямо. Объявляю заранее: геометрическое распределение —
это распределение БЕЗ ПАМЯТИ, и если оно подтвердится, это довод в пользу
механизма, у которого расстояние до следующего похожего слова не зависит
от того, сколько уже прошло.
"""
import sys, collections, math, random, statistics as st
sys.path.insert(0,"scripts")
import measures as M

VL=M.load()
chars_per_line=st.mean(sum(len(w) for w in l)+len(l)-1 for l in VL)
print("="*96); print(f"1. ДАЛЬНИЕ КОРРЕЛЯЦИИ ЗНАКОВ (средняя длина строки {chars_per_line:.1f} знаков)"); print("="*96)
S=[]
for l in VL:
    for i,w in enumerate(l):
        S+=list(w)
        if i<len(l)-1: S.append(" ")
    S.append(" ")
n=len(S); freq=collections.Counter(S)
def acorr(seq, lags):
    idx=collections.defaultdict(set)
    for i,c in enumerate(seq): idx[c].add(i)
    out={}
    for lag in lags:
        hit=tot=0
        for c,ii in idx.items():
            if len(ii)<300: continue
            p=len(ii)/len(seq)
            h=sum(1 for i in ii if i+lag in ii)
            hit+=h; tot+=len(ii)*p
        out[lag]=hit/tot
    return out
LAGS=[1,2,5,10,20,40,60,70,72,74,76,80,90,100,120,150]
a=acorr(S,LAGS)
rnd=random.Random(11); SH=S[:]; rnd.shuffle(SH)
b=acorr(SH,LAGS)
print(f"  {'лаг':>5s} {'рукопись':>10s} {'перемешка':>11s}")
for L in LAGS:
    mark=""
    if abs(L-chars_per_line)<6: mark="  ← длина строки"
    if L==72: mark+="  ← 72 Шиннера"
    print(f"  {L:5d} {a[L]:10.4f} {b[L]:11.4f}{mark}")

print("\n"+"="*96); print("2. РАССТОЯНИЯ МЕЖДУ ПОХОЖИМИ СЛОВАМИ: геометрическое ли"); print("="*96)
toks=M.tokens(VL); T=set(toks)
nb=M.nbrs(T)
pos=collections.defaultdict(list)
for i,w in enumerate(toks): pos[w].append(i)
d=collections.Counter()
for i,w in enumerate(toks):
    best=None
    for v in nb.get(w,()):
        for j in pos[v]:
            if j>i and (best is None or j-i<best): best=j-i
    if best is not None and best<=60: d[best]+=1
tot=sum(d.values())
print(f"  расстояний до ближайшего ПОХОЖЕГО слова учтено: {tot}")
print(f"  {'d':>4s} {'доля':>9s} {'геометр.':>10s} {'отношение':>10s}")
p_hat=1/st.mean([k for k,v in d.items() for _ in range(v)])
for k in list(range(1,11))+[15,20,30,40]:
    obs=d[k]/tot; exp=p_hat*(1-p_hat)**(k-1)
    print(f"  {k:4d} {obs:9.4f} {exp:10.4f} {obs/exp if exp>0 else float('nan'):9.2f}")
print(f"\n  оценка p = {p_hat:.4f}, среднее расстояние {1/p_hat:.1f}")
chi=sum((d[k]/tot-p_hat*(1-p_hat)**(k-1))**2/(p_hat*(1-p_hat)**(k-1)) for k in range(1,21))
print(f"  хи2 к геометрическому по первым 20 расстояниям: {chi*tot:.0f}")
print("  (для сравнения — то же на перемешанном потоке слов:)")
sh=toks[:]; random.Random(4).shuffle(sh)
pos2=collections.defaultdict(list)
for i,w in enumerate(sh): pos2[w].append(i)
d2=collections.Counter()
for i,w in enumerate(sh):
    best=None
    for v in nb.get(w,()):
        for j in pos2[v]:
            if j>i and (best is None or j-i<best): best=j-i
    if best is not None and best<=60: d2[best]+=1
t2=sum(d2.values()); p2=1/st.mean([k for k,v in d2.items() for _ in range(v)])
chi2=sum((d2[k]/t2-p2*(1-p2)**(k-1))**2/(p2*(1-p2)**(k-1)) for k in range(1,21))
print(f"  перемешка: p = {p2:.4f}, хи2 = {chi2*t2:.0f}")
