# -*- coding: utf-8 -*-
import json, collections, statistics as st, math, os, random
exec(open("scripts/seg.py").read().split('print("="*100); print("ШИРОКИЙ')[0])
VOYf=[w for l in VL for w in l]
print("="*100); print("ЗАВИСИМОСТЬ МЕРЫ ОТ ОБЪЁМА (на больших корпусах, 8 подвыборок на точку)"); print("="*100)
print(f"  {'корпус':>14s} "+" ".join(f"{str(n//1000)+'k':>9s}" for n in (4000,6000,12000,25000,50000,100000)))
def at_size(flat,n,B=8,seed=0):
    if len(flat)<n: return float('nan')
    v=[]
    for b in range(B):
        i=random.Random(seed+b).randrange(0,len(flat)-n+1)
        v.append(rank_corr(relines(flat[i:i+n], [x for x in LENS])))
    return st.mean(v)
BIG=[("ВОЙНИЧ",VOYf)]
for fn in ["english","latin","scr_tanakh","scr_vulgata","g_herbal","scr_quran"]:
    BIG.append((fn,open("ref/%s.clean"%fn,encoding="utf-8",errors="ignore").read().split()))
for nm,f in BIG:
    cells=[]
    for n in (4000,6000,12000,25000,50000,100000):
        v=at_size(f,n); cells.append(f"{v:+9.4f}" if v==v else "        —")
    print(f"  {nm:>14s} "+" ".join(cells))
print("\n"+"="*100); print("ВСЕ КОРПУСА НА ЕДИНОМ РАЗМЕРЕ 6000 СЛОВ (12 подвыборок, ±sd)"); print("="*100)
res=[]
def at6(flat,n=6000,B=12,seed=5):
    if len(flat)<n: return None
    v=[]
    for b in range(B):
        i=random.Random(seed+b).randrange(0,len(flat)-n+1)
        v.append(rank_corr(relines(flat[i:i+n],[x for x in LENS])))
    return st.mean(v), st.stdev(v)
r=at6(VOYf); res.append(("ВОЙНИЧ",r[0],r[1]))
for fn in sorted(os.listdir("ref")):
    if not fn.endswith(".clean"): continue
    w=open("ref/"+fn,encoding="utf-8",errors="ignore").read().split()
    x=at6(w)
    if x: res.append((fn[:-6],x[0],x[1]))
res.sort(key=lambda z:z[1])
for nm,m,s in res:
    mk=" ←ВОЙНИЧ" if nm=="ВОЙНИЧ" else ""
    print(f"  {nm:>14s} {m:+8.4f} ± {s:.4f}{mk}")
pos=[x for x in res if x[1]>0]
print(f"\n  корпусов с положительным знаком: {len(pos)} из {len(res)} — "+", ".join(f"{n} ({m:+.3f})" for n,m,_ in pos))
