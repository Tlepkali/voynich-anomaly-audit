# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys, math
exec(open("scripts/grid.py").read().split('print(f"ядер:')[0])
CV=rewrite(VL,rV); CL=rewrite(LL,rL)
print("="*112); print("ДЛИНЫ ЯДЕР"); print("="*112)
for nm,W in [("Войнич",CORES_V),("латынь",CORES_L)]:
    c=collections.Counter(len(w) for w in W)
    print(f"  {nm:>8s} всего {len(W):5d}: "+" ".join(f"дл{k}·{c[k]}" for k in sorted(c) if c[k]>=20))
def mi4(words):
    sub=[w for w in words if len(w)==4]
    if len(sub)<150: return float('nan')
    j=collections.Counter()
    for w in sub:
        for i,ch in enumerate(w): j[(ch,i)]+=1
    T=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (g,i),c in j.items(): pg[g]+=c; pp[i]+=c
    return sum(c/T*math.log2((c/T)/((pg[g]/T)*(pp[i]/T))) for (g,i),c in j.items())
def excess(words,B=15,seed=50):
    o=mi4(words)
    if o!=o: return float('nan'),float('nan'),float('nan')
    v=[]
    for s_ in range(B):
        rnd=random.Random(seed+s_); sh=[]
        for w in words:
            c=list(w); rnd.shuffle(c); sh.append("".join(c))
        x=mi4(sh)
        if x==x: v.append(x)
    m=st.mean(v) if v else float('nan')
    return o,m,(o/m if m else float('nan'))
print("\n"+"="*112); print("СЛОТОВОСТЬ НА ДЛИНЕ 4: ТИПЫ против ТОКЕНОВ — единица меняет ответ"); print("="*112)
print(f"  {'что мерим':>34s} {'MI':>7s} {'при перемешивании':>19s} {'избыток':>9s}")
sets=[("Войнич, ВСЕ типы",list(S)),("Войнич, ядра (типы)",CORES_V),
      ("латынь, ВСЕ типы",list(SL)),("латынь, ядра (типы)",CORES_L),
      ("перемешка Войнича, ядра",CORES_SH)]
for nm,W in sets:
    o,m,r=excess(W)
    if o!=o: print(f"  {nm:>34s}   — слов длины 4 мало"); continue
    print(f"  {nm:>34s} {o:7.3f} {m:19.3f} {r:8.2f}×")
print()
for nm,L in [("Войнич, исходный ТЕКСТ (токены)",VL),("Войнич, ядерный ТЕКСТ (токены)",CV),
             ("латынь, исходный ТЕКСТ (токены)",LL),("латынь, ядерный ТЕКСТ (токены)",CL)]:
    f=[w for l in L for w in l]
    o,m,r=excess(f,B=6)
    if o!=o: continue
    print(f"  {nm:>34s} {o:7.3f} {m:19.3f} {r:8.2f}×")
print("\n"+"="*112); print("ОТКУДА БЕРЁТСЯ РАЗНИЦА: насколько частотное распределение ядер перекошено"); print("="*112)
for nm,L in [("Войнич, ядерный текст",CV),("латынь, ядерный текст",CL)]:
    f=[w for l in L for w in l if len(w)==4]
    c=collections.Counter(f)
    top=c.most_common(5); cov=sum(v for _,v in top)/max(len(f),1)
    print(f"  {nm:>24s}: слов длины 4 {len(f):6d}, типов {len(c):5d}, "
          f"топ-5 покрывают {cov:5.1%} | "+" ".join(f"{w}·{n}" for w,n in top[:5]))
