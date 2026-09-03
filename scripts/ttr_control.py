# -*- coding: utf-8 -*-
"""Сводится ли жанровый сдвиг к разнице TTR? Регрессия меры на TTR по всем корпусам ≥34k."""
import json, collections, statistics as st, math, random, os
exec(open("scripts/genre_effect.py").read().split("PAIRS=")[0])
def stats(path,n=34000,B=10,seed=7):
    if not os.path.exists(path): return None
    f=open(path,encoding="utf-8",errors="ignore").read().split()
    if len(f)<n: return None
    r=[];t=[]
    for b in range(B):
        i=random.Random(seed+b).randrange(0,len(f)-n+1); s=f[i:i+n]
        r.append(rc(relines(s))); t.append(len(set(s))/n)
    return st.mean(r), st.mean(t)
V=[w for l in VL for w in l]
rows=[("ВОЙНИЧ", stats.__wrapped__ if False else None)]
def voy():
    r=[];t=[]
    for b in range(10):
        i=random.Random(7+b).randrange(0,len(V)-34000+1); s=V[i:i+34000]
        r.append(rc(relines(s))); t.append(len(set(s))/34000)
    return st.mean(r), st.mean(t)
DAT=[("ВОЙНИЧ",)+voy()]
for fn in sorted(os.listdir("ref")):
    if not fn.endswith(".clean"): continue
    x=stats("ref/"+fn)
    if x: DAT.append((fn[:-6],)+x)
xs=[d[2] for d in DAT]; ys=[d[1] for d in DAT]
mx,my=st.mean(xs),st.mean(ys)
a=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs); b=my-a*mx
R=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.sqrt(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
print("="*96); print(f"МЕРА ПРОТИВ TTR НА 34 ТЫС. СЛОВ, {len(DAT)} корпусов  (r = {R:+.3f}, наклон {a:+.3f})"); print("="*96)
print(f"  {'корпус':>16s} {'TTR@34k':>8s} {'мера':>9s} {'остаток':>9s} {'в sd':>7s}")
resid=[(nm,y-(a*t+b),t,y) for nm,y,t in DAT]
sd=st.pstdev([r for _,r,_,_ in resid])
for nm,rr,t,y in sorted(resid,key=lambda z:-z[1]):
    mk=" ←" if nm in ("ВОЙНИЧ","wiki_mn") else ""
    print(f"  {nm:>16s} {t:8.3f} {y:+9.4f} {rr:+9.4f} {rr/sd:+7.2f}{mk}")
print(f"\n  стандартное отклонение остатков: {sd:.4f}")
w=[d for d in resid if d[0]=="ВОЙНИЧ"][0]; m=[d for d in resid if d[0]=="wiki_mn"]
if m:
    m=m[0]
    print(f"  ВОЙНИЧ: TTR {w[2]:.3f}, мера {w[3]:+.4f}, остаток {w[1]:+.4f} ({w[1]/sd:+.2f} sd)")
    print(f"  монгольский: TTR {m[2]:.3f}, мера {m[3]:+.4f}, остаток {m[1]:+.4f} ({m[1]/sd:+.2f} sd)")
    print(f"\n  {'ПОСЛЕ поправки на TTR рукопись ВЫШЕ' if w[1]>m[1] else 'ПОСЛЕ поправки на TTR монгольский ВЫШЕ'}"
          f" — разница {abs(w[1]-m[1]):.4f} = {abs(w[1]-m[1])/sd:.2f} sd")
