# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys, math
exec(open("scripts/order2.py").read().split('print("="*112); print(f"ВЫРОВНЕННЫЙ')[0])
print("="*104); print(f"ПОВТОРЯЮЩИЕСЯ БИГРАММЫ, ВЫРОВНЕННЫЙ ОБЪЁМ {NM} СЛОВ"); print("="*104)
print(f"  {'корпус':>14s} {'набл.':>7s} {'окно 10':>16s} {'окно 50':>16s}")
for nm,f in CORP:
    o,_=rep_bigram(f)
    a=st.mean(rep_bigram(wshuf(f,10,s))[0] for s in range(6))
    b=st.mean(rep_bigram(wshuf(f,50,s))[0] for s in range(6))
    print(f"  {nm:>14s} {o:7.3f} {a:9.3f} ({o/a:4.2f}×) {b:9.3f} ({o/b:4.2f}×)")
print("\n"+"="*104); print("УСТОЙЧИВОСТЬ К ГРАНИЦАМ КОРЗИН: нормированная MI при разных разбиениях"); print("="*104)
def buck2(flat,cuts):
    c=collections.Counter(flat); order=[w for w,_ in c.most_common()]; b={}
    for i,w in enumerate(order):
        j=0
        while j<len(cuts) and i>=cuts[j]: j+=1
        b[w]=j
    return b
SETS=[("10/50/200/1000",[10,50,200,1000]),("5/25/100/500",[5,25,100,500]),
      ("20/100/500/2000",[20,100,500,2000]),("две корзины: 50",[50]),("три: 20/200",[20,200])]
print(f"  {'корпус':>14s} "+" ".join(f"{n:>17s}" for n,_ in SETS))
for nm,f in CORP:
    cells=[]
    for _,cu in SETS:
        b=buck2(f,cu); cc=collections.Counter(b[w] for w in f); n=len(f)
        H=-sum(v/n*math.log2(v/n) for v in cc.values())
        cells.append(f"{class_mi(f,b)/max(H,1e-9):17.4f}")
    print(f"  {nm:>14s} "+" ".join(cells))
print("\n"+"="*104); print("ПРЯМАЯ ФОРМУЛИРОВКА: чередуются ли частые и редкие слова"); print("="*104)
print("  корреляция логарифма ранга соседних слов; у языка ожидается ОТРИЦАТЕЛЬНАЯ (частое ↔ редкое)")
print(f"  {'корпус':>14s} {'r(соседи)':>10s} {'при окне 50':>13s} {'избыток':>9s}")
def rankcorr(flat,W=None,seed=0):
    g=wshuf(flat,W,seed) if W else flat
    c=collections.Counter(g); rk={w:i+1 for i,(w,_) in enumerate(c.most_common())}
    L=cut(g); xs=[];ys=[]
    for l in L:
        for i in range(len(l)-1):
            xs.append(math.log(rk[l[i]])); ys.append(math.log(rk[l[i+1]]))
    mx,my=st.mean(xs),st.mean(ys)
    num=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
    den=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    return num/den if den else 0
for nm,f in CORP:
    o=rankcorr(f); s=st.mean(rankcorr(f,50,x) for x in range(5))
    print(f"  {nm:>14s} {o:10.4f} {s:13.4f} {o-s:+9.4f}")
