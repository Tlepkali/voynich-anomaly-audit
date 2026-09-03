# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys, math
exec(open("scripts/order5.py").read().split('print("="*104); print("СРАВНЕНИЕ КАК С КАК')[0])
def pairs_of(L,drop=None):
    f=[w for l in L for w in l]
    c=collections.Counter(f); rk={w:i+1 for i,(w,_) in enumerate(c.most_common())}
    out=[]
    for li,l in enumerate(L):
        for i in range(len(l)-1):
            if drop and drop(l[i],l[i+1]): continue
            out.append((li, math.log(rk[l[i]]), math.log(rk[l[i+1]])))
    return out
def corr(ps):
    if len(ps)<100: return float('nan')
    xs=[x for _,x,_ in ps]; ys=[y for _,_,y in ps]
    mx,my=st.mean(xs),st.mean(ys)
    num=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
    den=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    return num/den if den else 0
def boot_lines(L,drop=None,B=600):
    ps=pairs_of(L,drop)                      # ранги считаются ОДИН раз, на полном корпусе
    bl=collections.defaultdict(list)
    for t in ps: bl[t[0]].append(t)
    keys=list(bl); rnd=random.Random(81); out=[]
    for _ in range(B):
        s=[]
        for _ in range(len(keys)): s+=bl[keys[rnd.randrange(len(keys))]]
        r=corr(s)
        if r==r: out.append(r)
    out.sort(); return corr(ps), out[int(.025*len(out))], out[int(.975*len(out))]
print("="*100); print("ИСПРАВЛЕННЫЙ БУТСТРАП: ранги фиксированы по полному корпусу, перевыбираются только строки"); print("="*100)
print(f"  {'текст':>28s} {'r':>9s} {'95 % ДИ':>20s}")
for lab,L in [("Войнич, исходный",VL),("Войнич в ядрах",CV),("латынь, исходная",LL),("латынь в ядрах",CL)]:
    for tag,dr in [("все пары",None),("без соседей ≤1",near)]:
        r,lo,hi=boot_lines(L,dr)
        print(f"  {(lab+', '+tag):>28s} {r:9.4f} [{lo:+8.4f}; {hi:+8.4f}]")
    print()
