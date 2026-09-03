# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys, math
exec(open("scripts/coretext.py").read().split("root,frac=build_map")[0])
S=set(VOY)
lw=open("ref/latin.clean").read().split()
LL=[];p=0
for l in VL:
    if p+len(l)>len(lw): break
    LL.append(lw[p:p+len(l)]); p+=len(l)
SL=set(w for l in LL for w in l)
rV,fV=build_map(S,15); rL,fL=build_map(SL,400)
CV=rewrite(VL,rV); CL=rewrite(LL,rL)
def mi_fixed(words,n):
    sub=[w for w in words if len(w)==n]
    if len(sub)<300: return float('nan'),len(sub)
    j=collections.Counter()
    for w in sub:
        for i,c in enumerate(w): j[(c,i)]+=1
    T=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (g,i),c in j.items(): pg[g]+=c; pp[i]+=c
    return sum(c/T*math.log2((c/T)/((pg[g]/T)*(pp[i]/T))) for (g,i),c in j.items()), len(sub)
print("="*104); print("СЛОТОВОСТЬ НА ФИКСИРОВАННОЙ ДЛИНЕ СЛОВА (снимаем механику укорочения)"); print("="*104)
print(f"  {'текст':>26s} {'ср.длина':>9s} | "+" ".join(f"{'дл '+str(n):>13s}" for n in (3,4,5,6)))
for lab,L in [("Войнич, как есть",VL),(f"Войнич в ядрах ({fV:.0%})",CV),("латынь, как есть",LL),(f"латынь в ядрах ({fL:.0%})",CL)]:
    f=[w for l in L for w in l]; cells=[]
    for n in (3,4,5,6):
        v,c=mi_fixed(f,n); cells.append(f"{v:.3f} ({c//1000}k)" if v==v else "      —      ")
    print(f"  {lab:>26s} {st.mean(len(w) for w in f):9.2f} | "+" ".join(f"{c:>13s}" for c in cells))
print("\n"+"="*104); print("УСЛОВНАЯ ЭНТРОПИЯ h2 НА СЛОВАХ ОДНОЙ ДЛИНЫ (только слова длины 4, без пробелов)"); print("="*104)
def h2_fixed(words,n=4):
    sub=[w for w in words if len(w)==n]
    if len(sub)<300: return float('nan')
    ch=[]
    for w in sub: ch.extend(list(w))
    uni=collections.Counter(ch); T=len(ch)
    h1=-sum(c/T*math.log2(c/T) for c in uni.values())
    bi=collections.Counter(zip(ch,ch[1:])); M=sum(bi.values())
    return -sum(c/M*math.log2(c/M) for c in bi.values())-h1
print(f"  {'текст':>26s} {'h2 на словах длины 4':>22s}")
for lab,L in [("Войнич, как есть",VL),(f"Войнич в ядрах",CV),("латынь, как есть",LL),(f"латынь в ядрах",CL)]:
    v=h2_fixed([w for l in L for w in l])
    print(f"  {lab:>26s} {v:22.2f}" if v==v else f"  {lab:>26s} {'—':>22s}")
print("\n"+"="*104); print("ИТОГ: что обвес объясняет, а что нет"); print("="*104)
def j1(L):
    def pr(LL,k): return [(x[-k:],y[:k]) for l in LL for x,y in zip(l,l[1:])]
    o=MI(pr(L,1)); flat=[w for l in L for w in l]; rnd=random.Random(9); s=0.0
    for _ in range(5):
        sh=flat[:]; rnd.shuffle(sh); i=0; SH=[]
        for l in L: SH.append(sh[i:i+len(l)]); i+=len(l)
        s+=MI(pr(SH,1))/5
    return o-s
def nearr(L): return adjr(L,near)
def samer(L): return adjr(L,lambda a,b:a==b)
print(f"  {'мера':>30s} {'Войнич':>8s} {'латынь':>8s} {'разрыв':>8s} | {'ядра В.':>8s} {'ядра л.':>8s} {'разрыв':>8s} {'':>4s}")
def line(nm,f,fmt="%.3f"):
    a,b,c,d=f(VL),f(LL),f(CV),f(CL)
    g1=a/b if b else float('nan'); g2=c/d if d else float('nan')
    verdict="СНЯТО" if abs(g2-1)<0.35*abs(g1-1) else ("частично" if abs(g2-1)<0.75*abs(g1-1) else "ОСТАЛОСЬ")
    print(f"  {nm:>30s} {fmt%a:>8s} {fmt%b:>8s} {g1:7.2f}× | {fmt%c:>8s} {fmt%d:>8s} {g2:7.2f}× {verdict:>10s}")
line("стык по 1 знаку", j1)
line("соседство одинаковых", samer, "%.2f")
line("соседство похожих", nearr, "%.2f")
line("слотовость на длине 4", lambda L: mi_fixed([w for l in L for w in l],4)[0])
line("h2 на словах длины 4", lambda L: h2_fixed([w for l in L for w in l]), "%.2f")
