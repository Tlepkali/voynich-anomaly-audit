# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys, math
exec(open("scripts/order2.py").read().split('print("="*112); print(f"ВЫРОВНЕННЫЙ')[0])
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
def rankcorr(flat,W=None,seed=0,drop=None):
    g=wshuf(flat,W,seed) if W else flat
    c=collections.Counter(g); rk={w:i+1 for i,(w,_) in enumerate(c.most_common())}
    L=cut(g); xs=[];ys=[]
    for l in L:
        for i in range(len(l)-1):
            if drop and drop(l[i],l[i+1]): continue
            xs.append(math.log(rk[l[i]])); ys.append(math.log(rk[l[i+1]]))
    if len(xs)<100: return float('nan'),0
    mx,my=st.mean(xs),st.mean(ys)
    num=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
    den=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    return (num/den if den else 0), len(xs)
print("="*110); print("ПОВТОРЯЮЩИЕСЯ БИГРАММЫ, ВЫРОВНЕННЫЙ ОБЪЁМ (все строки)"); print("="*110)
for nm,f in CORP:
    o,_=rep_bigram(f); b=st.mean(rep_bigram(wshuf(f,50,s))[0] for s in range(6))
    print(f"  {nm:>14s} набл. {o:.3f}, при окне 50 {b:.3f} — отношение {o/b:.2f}×")
print("\n"+"="*110); print("КОНТРОЛЬ: не пересказ ли это отсутствия запрета на повтор"); print("="*110)
print(f"  {'корпус':>14s} {'все пары':>10s} {'без одинаковых':>15s} {'без соседей ≤1':>15s} {'пар осталось':>13s}")
for nm,f in CORP:
    a,_=rankcorr(f)
    b,_=rankcorr(f,drop=lambda x,y:x==y)
    c,n=rankcorr(f,drop=near)
    print(f"  {nm:>14s} {a:10.4f} {b:15.4f} {c:15.4f} {n:13d}")
print("\n"+"="*110); print("УСТОЙЧИВОСТЬ ПО КОНТУРАМ, РАЗДЕЛАМ И НА ЯДЕРНОМ ТЕКСТЕ"); print("="*110)
PG=json.load(open("parsed.json"))["pages"]
rows=[r for r in json.load(open("parsed.json"))["rows"] if r["locus"]=="P"]
def sub(pred):
    out=[]
    for r in rows:
        m=PG.get(r["page"],{}); ws=[w for w in r["words"] if '?' not in w]
        if len(ws)>=3 and pred(m): out+=ws
    return out
print(f"  {'выборка':>22s} {'слов':>7s} {'r(соседи)':>10s} {'без соседей ≤1':>15s}")
for lab,pred in [("язык A",lambda m:m.get("L")=="A"),("язык B",lambda m:m.get("L")=="B"),
                 ("травник",lambda m:m.get("I")=="H"),("звёзды",lambda m:m.get("I")=="S"),
                 ("«банный»",lambda m:m.get("I")=="B")]:
    f=sub(pred)
    if len(f)<3000: continue
    a,_=rankcorr(f); c,_=rankcorr(f,drop=near)
    print(f"  {lab:>22s} {len(f):7d} {a:10.4f} {c:15.4f}")
try:
    exec(open("scripts/coretext.py").read().split("root,frac=build_map")[0])
    rV,fV=build_map(set(VOY),15); CV=[[rV.get(w,w) for w in l] for l in VL]
    f=[w for l in CV for w in l]
    a,_=rankcorr(f); c,_=rankcorr(f,drop=near)
    print(f"  {'ядерный текст':>22s} {len(f):7d} {a:10.4f} {c:15.4f}")
except Exception as e: print("  ядерный текст:", e)
