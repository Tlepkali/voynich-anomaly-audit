# -*- coding: utf-8 -*-
"""Контраст типов и токенов на СЫРОМ тексте — без разложения."""
import json, collections, math, random, statistics as st
def load(n):
    d=json.load(open(f"data/parsed_{n}.json"))
    L=[[w for w in r["words"] if '?' not in w] for r in d["rows"] if r["locus"]=="P"]
    return [l for l in L if len(l)>=3]
VL=load("ZL3b-n"); LENS=[len(l) for l in VL]
lw=open("ref/latin.clean").read().split(); LL=[];p=0
for n in LENS:
    if p+n>len(lw): break
    LL.append(lw[p:p+n]); p+=n
def mi4(seq):
    sub=[w for w in seq if len(w)==4]
    if len(sub)<150: return float('nan')
    j=collections.Counter()
    for w in sub:
        for i,c in enumerate(w): j[(c,i)]+=1
    n=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (g,i),c in j.items(): pg[g]+=c; pp[i]+=c
    return sum(c/n*math.log2((c/n)/((pg[g]/n)*(pp[i]/n))) for (g,i),c in j.items())
def excess(seq,B=10,seed=50):
    o=mi4(seq); v=[]
    for s in range(B):
        r=random.Random(seed+s); sh=[]
        for w in seq:
            c=list(w); r.shuffle(c); sh.append("".join(c))
        x=mi4(sh)
        if x==x: v.append(x)
    return o, (o/st.mean(v) if v else float('nan'))
def h2(seq,n=4):
    sub=[w for w in seq if len(w)==n]
    if len(sub)<150: return float('nan')
    ch=[]
    for w in sub: ch.extend(list(w))
    u=collections.Counter(ch); T=len(ch)
    h1=-sum(c/T*math.log2(c/T) for c in u.values())
    bi=collections.Counter(zip(ch,ch[1:])); M=sum(bi.values())
    return -sum(c/M*math.log2(c/M) for c in bi.values())-h1
print("="*104); print("ТИПЫ ПРОТИВ ТОКЕНОВ НА СЫРОМ ТЕКСТЕ (длина слова 4, без всякого разложения)"); print("="*104)
print(f"  {'что мерим':>34s} {'Войнич':>10s} {'латынь':>10s} {'разрыв':>9s}")
rows=[]
for lab,fn in [("токены",lambda L:[w for l in L for w in l]),("типы",lambda L:sorted({w for l in L for w in l}))]:
    v=fn(VL); l=fn(LL)
    ov,ev=excess(v); ol,el=excess(l)
    print(f"  {'слотовость: сырая MI, '+lab:>34s} {ov:10.3f} {ol:10.3f} {ov/ol:8.2f}×")
    print(f"  {'слотовость: избыток над перемешкой, '+lab:>34s} {ev:9.2f}× {el:9.2f}× {ev/el:8.2f}×")
    hv,hl=h2(v),h2(l)
    print(f"  {'условная энтропия h2, '+lab:>34s} {hv:10.2f} {hl:10.2f} {hv/hl:8.2f}×")
    rows.append((lab,ov,ol,ev,el,hv,hl))
    print()
print("="*104); print("ПОЧЕМУ ЕДИНИЦЫ РАСХОДЯТСЯ: перекос частот на длине 4"); print("="*104)
for lab,L in [("Войнич",VL),("латынь",LL)]:
    f=[w for l in L for w in l if len(w)==4]; c=collections.Counter(f)
    top=c.most_common(5)
    print(f"  {lab:>8s}: слов длины 4 {len(f):6d}, типов {len(c):5d}, "
          f"топ-5 покрывают {sum(n for _,n in top)/len(f):5.1%} | "+" ".join(f"{w}·{n}" for w,n in top))
