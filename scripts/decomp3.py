# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, math
exec(open("scripts/decomp2.py").read().split('print("="*106)')[0])
TV=sorted({w for l in VL for w in l}); TL=sorted({w for l in LL for w in l})
print("="*100); print("ЧУВСТВИТЕЛЬНОСТЬ ВТОРОГО АЛГОРИТМА К ЕГО ПАРАМЕТРАМ"); print("="*100)
print(f"  {'min_stems':>10s} {'min_sufs':>9s} {'Войнич':>9s} {'латынь':>9s} {'отношение':>10s}")
for ms in (2,3,5,10):
    for mf in (2,3,4):
        _,a=decompose(TV,ms,mf); _,b=decompose(TL,ms,mf)
        print(f"  {ms:10d} {mf:9d} {a:8.1%} {b:8.1%} {a/max(b,1e-9):9.2f}×")
print("\n"+"="*100); print("В ЧЁМ РАЗНИЦА АЛГОРИТМОВ: зависит ли критерий от ПЛОТНОСТИ словаря"); print("="*100)
def alg1_rate(T,k=15):
    S=set(T); pre=collections.Counter(); suf=collections.Counter()
    for w in T:
        for n in (1,2,3):
            if len(w)>n: pre[w[:n]]+=1; suf[w[-n:]]+=1
    P=[a for a,_ in pre.most_common(k)]; U=[a for a,_ in suf.most_common(k)]
    d=0
    for w in S:
        if any(w.startswith(a) and w[len(a):] in S and len(w[len(a):])>=2 for a in P) or \
           any(w.endswith(a) and w[:-len(a)] in S and len(w[:-len(a)])>=2 for a in U): d+=1
    return d/len(S)
def shuf_types(T,seed=0):
    r=random.Random(seed); out=set()
    for w in T:
        c=list(w); r.shuffle(c); out.add("".join(c))
    return sorted(out)
print("  Алгоритм 1 требует, чтобы ОСТАТОК был словом словаря. У рукописи словарь плотный")
print("  (9,63 соседа на тип против 1,0 у латыни), значит остаток попадает в словарь ЧАЩЕ")
print("  почти по построению. Проверка: доля вывода против плотности окрестности.\n")
print(f"  {'корпус':>28s} {'соседей/тип':>12s} {'алг.1':>8s} {'алг.2':>8s}")
def dens(T):
    nb=nbrs(set(T)); return st.mean(len(nb.get(w,())) for w in T)
for lab,T in [("Войнич",TV),("Войнич, знаки перемешаны",shuf_types(TV)),("латынь",TL),("латынь, знаки перемешаны",shuf_types(TL))]:
    _,a2=decompose(T)
    print(f"  {lab:>28s} {dens(T):12.2f} {alg1_rate(T):7.1%} {a2:7.1%}")
