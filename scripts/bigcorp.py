# -*- coding: utf-8 -*-
"""Ключевой опыт: держится ли положительный знак у монгольского, иврита и санскрита
на объёме рукописи — или тает, как у Танаха."""
import json, collections, statistics as st, math, os, random
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]
LENS=[len(l) for l in VL]; NV=sum(LENS)
def relines(flat):
    out=[];k=0
    for n in LENS:
        if k+n>len(flat): break
        out.append(flat[k:k+n]); k+=n
    return out
def corr(P):
    xs=[a for a,_ in P]; ys=[b for _,b in P]
    mx,my=st.mean(xs),st.mean(ys)
    n=sum((a-mx)*(b-my) for a,b in zip(xs,ys)); d=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    return n/d if d else 0
def rank_corr(L):
    f=[w for l in L for w in l]; c=collections.Counter(f)
    rk={w:i+1 for i,(w,_) in enumerate(c.most_common())}
    return corr([(math.log(rk[l[i]]),math.log(rk[l[i+1]])) for l in L for i in range(len(l)-1)])
def at(flat,n,B=10,seed=7):
    if len(flat)<n: return None
    v=[]
    for b in range(B):
        i=random.Random(seed+b).randrange(0,len(flat)-n+1)
        v.append(rank_corr(relines(flat[i:i+n])))
    return st.mean(v), st.stdev(v) if len(v)>1 else 0.0
VOY=[w for l in VL for w in l]
SIZES=[6000,12000,25000,34000,60000,120000,200000]
print("="*116); print(f"ЗНАК КАК ФУНКЦИЯ ОБЪЁМА (рукопись = {NV} слов; 10 подвыборок на точку)"); print("="*116)
print(f"  {'корпус':>16s} {'всего':>8s} "+" ".join(f"{str(n//1000)+'k':>10s}" for n in SIZES))
rows=[("ВОЙНИЧ",VOY)]
for fn in sorted(os.listdir("ref")):
    if not fn.endswith(".clean"): continue
    w=open("ref/"+fn,encoding="utf-8",errors="ignore").read().split()
    if len(w)>=34000: rows.append((fn[:-6],w))
for nm,f in rows:
    cells=[]
    for n in SIZES:
        r=at(f,n)
        cells.append(f"{r[0]:+10.4f}" if r else "         —")
    print(f"  {nm:>16s} {len(f):8d} "+" ".join(cells))
print("\n  ключевой вопрос: сохраняют ли монгольский, иврит и санскрит положительный знак")
print("  на 34 тыс. слов — или тают, как Танах (+0,049 на 4k → +0,004 на 100k)")
