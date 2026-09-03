# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys, math
exec(open("scripts/grid.py").read().split('print(f"ядер:')[0])
print("="*104); print("СКОЛЬКО ЯДЕР КАКОЙ ДЛИНЫ (проверяю, была ли у решётки вообще выборка)"); print("="*104)
for nm,W in [("Войнич",CORES_V),("латынь",CORES_L)]:
    c=collections.Counter(len(w) for w in W)
    print(f"  {nm:>8s} всего {len(W):5d}: "+" ".join(f"дл{k}·{c[k]}" for k in sorted(c) if c[k]>=20))
print("\n"+"="*104); print("ЧЕМ ТОГДА ДЕРЖИТСЯ СЛОТОВОСТЬ ЯДЕР: позиционная сегрегация знаков"); print("="*104)
print("  для каждого знака — доля вхождений в первой половине слова; 0,5 = знак безразличен к позиции")
def segregation(words,minn=60):
    pos=collections.defaultdict(lambda:[0,0])
    for w in words:
        n=len(w)
        if n<3: continue
        for i,c in enumerate(w):
            pos[c][1]+=1
            if i < n/2: pos[c][0]+=1
    out=[(v[0]/v[1],c,v[1]) for c,v in pos.items() if v[1]>=minn]
    return sorted(out)
def summarize(words,lab,minn=60):
    s=segregation(words,minn)
    if len(s)<6: print(f"  {lab:>26s}  знаков мало"); return None
    ext=sum(1 for f,_,_ in s if f<0.15 or f>0.85)
    print(f"  {lab:>26s} знаков {len(s):3d} | крайних (<15 % или >85 %): {ext:2d} = {ext/len(s):4.0%} | "
          f"медиана |откл. от 0,5| {st.median(abs(f-0.5) for f,_,_ in s):.3f}")
    return s
sv=summarize(CORES_V,"Войнич, ядра")
sl=summarize(CORES_L,"латынь, ядра")
ss=summarize(CORES_SH,"перемешка, ядра")
sf=summarize(list(S),"Войнич, ВСЕ типы")
if sv:
    print("\n  ядра рукописи, крайние знаки:")
    print("    только В НАЧАЛЕ: "+", ".join(f"{c}({f:.0%},n={n})" for f,c,n in sv if f>0.85))
    print("    только В КОНЦЕ : "+", ".join(f"{c}({f:.0%},n={n})" for f,c,n in sv if f<0.15))
if sl:
    print("\n  ядра латыни, крайние знаки:")
    a=[f"{c}({f:.0%})" for f,c,n in sl if f>0.85]; b=[f"{c}({f:.0%})" for f,c,n in sl if f<0.15]
    print("    только В НАЧАЛЕ: "+(", ".join(a) or "нет"))
    print("    только В КОНЦЕ : "+(", ".join(b) or "нет"))
print("\n"+"="*104); print("ПРОВЕРКА: объясняет ли сегрегация слотовость — считаю MI при перемешивании знаков ВНУТРИ слова"); print("="*104)
def mi_fixed(words,n):
    sub=[w for w in words if len(w)==n]
    if len(sub)<150: return float('nan')
    j=collections.Counter()
    for w in sub:
        for i,c in enumerate(w): j[(c,i)]+=1
    T=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (g,i),c in j.items(): pg[g]+=c; pp[i]+=c
    return sum(c/T*math.log2((c/T)/((pg[g]/T)*(pp[i]/T))) for (g,i),c in j.items())
print(f"  {'набор':>22s} {'MI на дл.4':>11s} {'то же, знаки в слове перемешаны':>33s} {'избыток':>9s}")
for nm,W in [("Войнич, ядра",CORES_V),("латынь, ядра",CORES_L),("Войнич, все типы",list(S))]:
    o=mi_fixed(W,4)
    if o!=o: continue
    vals=[]
    for s_ in range(15):
        rnd=random.Random(50+s_)
        sh=[]
        for w in W:
            c=list(w); rnd.shuffle(c); sh.append("".join(c))
        v=mi_fixed(sh,4)
        if v==v: vals.append(v)
    m=st.mean(vals)
    print(f"  {nm:>22s} {o:11.3f} {m:33.3f} {o/max(m,1e-9):8.2f}×")
