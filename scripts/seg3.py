# -*- coding: utf-8 -*-
import json, collections, statistics as st, math, os, random
exec(open("scripts/seg.py").read().split('print("="*100); print("ШИРОКИЙ')[0])
VOYf=[w for l in VL for w in l]
def sample(flat,n,seed):
    i=random.Random(seed).randrange(0,len(flat)-n+1); return flat[i:i+n]
def stats6(flat,n=6000,B=12,seed=5):
    if len(flat)<n: return None
    r=[];t=[]
    for b in range(B):
        s=sample(flat,n,seed+b); L=relines(s,[x for x in LENS])
        r.append(rank_corr(L)); t.append(len(set(s))/n)
    return st.mean(r), st.mean(t)
DAT=[("ВОЙНИЧ",)+stats6(VOYf)]
for fn in sorted(os.listdir("ref")):
    if not fn.endswith(".clean"): continue
    w=open("ref/"+fn,encoding="utf-8",errors="ignore").read().split()
    x=stats6(w)
    if x: DAT.append((fn[:-6],)+x)
print("="*96); print("НЕ ЕСТЬ ЛИ ЗНАК ПРОСТО ФУНКЦИЯ БОГАТСТВА СЛОВАРЯ"); print("="*96)
xs=[d[2] for d in DAT]; ys=[d[1] for d in DAT]
mx,my=st.mean(xs),st.mean(ys)
num=sum((a-mx)*(b-my) for a,b in zip(xs,ys)); den=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
R=num/den
print(f"  корреляция между TTR@6k и знаком меры по {len(DAT)} корпусам: r = {R:+.3f}")
print(f"\n  {'корпус':>14s} {'TTR@6k':>8s} {'мера':>9s}")
for nm,r,t in sorted(DAT,key=lambda z:z[2]):
    mk=" ←" if nm=="ВОЙНИЧ" else ""
    print(f"  {nm:>14s} {t:8.3f} {r:+9.4f}{mk}")
print("\n"+"="*96); print("ЧАСТНАЯ КОРРЕЛЯЦИЯ: остаётся ли Войнич особенным ПОСЛЕ поправки на TTR"); print("="*96)
a=(sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs))
b=my-a*mx
print(f"  линия регрессии: мера = {a:+.4f}·TTR {b:+.4f}")
resid=[(nm, y-(a*t+b)) for nm,y,t in DAT]
resid.sort(key=lambda z:z[1])
sd=st.pstdev([r for _,r in resid])
print(f"  стандартное отклонение остатков: {sd:.4f}\n")
for nm,rr in resid:
    mk=" ←" if nm=="ВОЙНИЧ" else ""
    print(f"  {nm:>14s} остаток {rr:+8.4f}  ({rr/sd:+5.2f} sd){mk}")
