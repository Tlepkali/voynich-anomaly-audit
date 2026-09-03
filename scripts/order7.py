# -*- coding: utf-8 -*-
import json, collections, statistics as st, math, os, sys, random
exec(open("scripts/order_check.py").read().split('print(f"  {\'корпус\'')[0])
def near(a,b):
    if a==b: return True
    la,lb=len(a),len(b)
    if abs(la-lb)>1: return False
    if la==lb:
        d=0
        for x,y in zip(a,b):
            if x!=y:
                d+=1
                if d>1: return False
        return d==1
    s_,l_=(a,b) if la<lb else (b,a)
    return any(l_[:i]+l_[i+1:]==s_ for i in range(len(l_)))
def pairs_of(L,drop=None):
    f=[w for l in L for w in l]; c=collections.Counter(f)
    rk={w:i+1 for i,(w,_) in enumerate(c.most_common())}
    out=collections.defaultdict(list)
    for li,l in enumerate(L):
        for i in range(len(l)-1):
            if drop and drop(l[i],l[i+1]): continue
            out[li].append((math.log(rk[l[i]]),math.log(rk[l[i+1]])))
    return out
def corr_of(bl):
    P=[p for v in bl.values() for p in v]
    return corr_pairs(P) if len(P)>=100 else float('nan')
def boot(bl,B=500,seed=81):
    keys=list(bl); rnd=random.Random(seed); out=[]
    for _ in range(B):
        s={}
        for i in range(len(keys)): s[i]=bl[keys[rnd.randrange(len(keys))]]
        r=corr_of(s)
        if r==r: out.append(r)
    out.sort(); return out[int(.025*len(out))], out[int(.975*len(out))]
def wshuf(L,W,seed):
    f=[w for l in L for w in l]; rnd=random.Random(seed)
    for i in range(0,len(f),W):
        b=f[i:i+W]; rnd.shuffle(b); f[i:i+W]=b
    out=[];k=0
    for l in L: out.append(f[k:k+len(l)]); k+=len(l)
    return out
CORP=[("Войнич",VL),("латынь",LL)]
for nm,fn in [("английский","english"),("немецкий","wiki_de"),("итальянский","wiki_it")]:
    p="ref/%s.clean"%fn
    if not os.path.exists(p): continue
    w=open(p).read().split(); X=[];q=0
    for n in LENS:
        if q+n>len(w): break
        X.append(w[q:q+n]); q+=n
    if sum(len(l) for l in X)>25000: CORP.append((nm,X))
sys.path.insert(0,"scripts"); sys.path.insert(0,".")
try:
    exec(open("scripts/oos.py").read().split("CORP=")[0]); M=model()
    if M: CORP.append(("МОДЕЛЬ",M))
except Exception as e: pass
print("="*104); print("КОРРЕЛЯЦИЯ ЛОГ-РАНГОВ СОСЕДНИХ СЛОВ, полный объём, три реализации сверены"); print("="*104)
print("  отрицательная = частое чередуется с редким (служебные и знаменательные); положительная = липнут подобные")
print(f"\n  {'корпус':>13s} {'слов':>6s} {'все пары':>10s} {'95 % ДИ':>20s} {'без соседей ≤1':>15s} {'95 % ДИ':>20s} {'окно 50':>9s}")
for nm,L in CORP:
    n=sum(len(l) for l in L)
    a=pairs_of(L); ra=corr_of(a); la,ha=boot(a)
    b=pairs_of(L,near); rb=corr_of(b); lb,hb=boot(b)
    sh=st.mean(corr_of(pairs_of(wshuf(L,50,s))) for s in range(4))
    print(f"  {nm:>13s} {n:6d} {ra:10.4f} [{la:+7.4f}; {ha:+7.4f}] {rb:15.4f} [{lb:+7.4f}; {hb:+7.4f}] {sh:9.4f}")
