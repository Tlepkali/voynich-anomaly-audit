# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys, math
exec(open("scripts/grid.py").read().split('print(f"ядер:')[0])
CV=rewrite(VL,rV); CL=rewrite(LL,rL)
def h2_of(words,n=4):
    sub=[w for w in words if len(w)==n]
    if len(sub)<150: return float('nan')
    ch=[]
    for w in sub: ch.extend(list(w))
    uni=collections.Counter(ch); T=len(ch)
    h1=-sum(c/T*math.log2(c/T) for c in uni.values())
    bi=collections.Counter(zip(ch,ch[1:])); M=sum(bi.values())
    return -sum(c/M*math.log2(c/M) for c in bi.values())-h1
print("="*104); print("УСЛОВНАЯ ЭНТРОПИЯ h2 НА ДЛИНЕ 4: та же проверка единицы"); print("="*104)
print(f"  {'что мерим':>36s} {'h2':>7s} {'слов':>7s}")
for nm,W in [("Войнич, ВСЕ типы",list(S)),("Войнич, ядра (типы)",CORES_V),
             ("латынь, ВСЕ типы",list(SL)),("латынь, ядра (типы)",CORES_L)]:
    v=h2_of(W); n=sum(1 for w in W if len(w)==4)
    print(f"  {nm:>36s} {v:7.2f} {n:7d}" if v==v else f"  {nm:>36s} {'—':>7s} {n:7d}")
print()
for nm,L in [("Войнич, исходный ТЕКСТ (токены)",VL),("Войнич, ядерный ТЕКСТ (токены)",CV),
             ("латынь, исходный ТЕКСТ (токены)",LL),("латынь, ядерный ТЕКСТ (токены)",CL)]:
    f=[w for l in L for w in l]; v=h2_of(f)
    print(f"  {nm:>36s} {v:7.2f} {sum(1 for w in f if len(w)==4):7d}")
print("\n"+"="*104); print("СВОДКА ПОСЛЕ ИСПРАВЛЕНИЯ ЕДИНИЦЫ (всё на ТИПАХ, длина 4)"); print("="*104)
print(f"  {'мера':>30s} {'В. все':>8s} {'В. ядра':>8s} {'лат. все':>9s} {'лат. ядра':>10s} {'вывод':>26s}")
def mi4(words):
    sub=[w for w in words if len(w)==4]
    if len(sub)<150: return float('nan')
    j=collections.Counter()
    for w in sub:
        for i,ch in enumerate(w): j[(ch,i)]+=1
    T=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (g,i),c in j.items(): pg[g]+=c; pp[i]+=c
    return sum(c/T*math.log2((c/T)/((pg[g]/T)*(pp[i]/T))) for (g,i),c in j.items())
def exc(W,B=15,seed=50):
    o=mi4(W); v=[]
    for s_ in range(B):
        rnd=random.Random(seed+s_); sh=[]
        for w in W:
            c=list(w); rnd.shuffle(c); sh.append("".join(c))
        x=mi4(sh)
        if x==x: v.append(x)
    return o/st.mean(v) if v else float('nan')
a,b,c,d=exc(list(S)),exc(CORES_V),exc(list(SL)),exc(CORES_L)
print(f"  {'слотовость, избыток':>30s} {a:7.2f}× {b:7.2f}× {c:8.2f}× {d:9.2f}× {'разрыв 2,12× → 1,00×':>26s}")
a2,b2,c2,d2=h2_of(list(S)),h2_of(CORES_V),h2_of(list(SL)),h2_of(CORES_L)
print(f"  {'условная энтропия h2':>30s} {a2:8.2f} {b2:8.2f} {c2:9.2f} {d2:10.2f} "
      f"{('разрыв %.2f× → %.2f×'%(a2/c2,b2/d2)):>26s}")
