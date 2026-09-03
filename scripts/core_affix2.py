# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys
exec(open("scripts/core_affix.py").read().split("CORP=[")[0])
CORP=[("Войнич",topN(VOY))]
for nm,fn in [("латынь","latin"),("английский","english"),("немецкий","wiki_de"),("итальянский","wiki_it")]:
    p="ref/%s.clean"%fn
    if os.path.exists(p): CORP.append((nm,topN(open(p).read().split())))
sys.path.insert(0,"scripts"); sys.path.insert(0,".")
exec(open("scripts/oos.py").read().split("CORP=")[0])
M=model()
if M: CORP.append(("МОДЕЛЬ",topN([w for l in M for w in l])))
CORP.append(("Войнич, знаки перемешаны",shuf_types(topN(VOY))))
NC=1800
def shape_of(T):
    T=set(T); nb=nbrs(T)
    def m(d):
        g=[len(nb.get(w,())) for w in T if len(w)==d]
        return st.mean(g) if len(g)>=12 else float('nan')
    a,b=m(3),m(5)
    return a,b,(b/a if a==a and b==b and a>0 else float('nan'))
print("="*112); print(f"ПРОФИЛЬ ЯДЕР НА ВЫРОВНЕННОМ СЛОВАРЕ ({NC} ядер, 25 подвыборок, бутстрап-интервал)"); print("="*112)
print(f"  {'корпус':>26s} {'ядер всего':>11s} {'дл3':>7s} {'дл5':>7s} {'дл5/дл3':>9s} {'95 % ДИ':>15s}")
for lab,T in CORP:
    d,c,dep,P,U=decompose(T)
    if len(c)<NC:
        print(f"  {lab:>26s} {len(c):11d}   — ядер меньше {NC}, выборка невозможна"); continue
    vals=[];a3=[];a5=[]
    for s in range(25):
        rnd=random.Random(200+s); sub=rnd.sample(c,NC)
        x,y,r=shape_of(sub)
        if r==r: vals.append(r); a3.append(x); a5.append(y)
    vals.sort()
    lo,hi=vals[max(0,int(.025*len(vals)))],vals[min(len(vals)-1,int(.975*len(vals)))]
    print(f"  {lab:>26s} {len(c):11d} {st.mean(a3):7.1f} {st.mean(a5):7.1f} {st.mean(vals):9.2f} [{lo:5.2f}; {hi:5.2f}]")
print("\n"+"="*112); print("ТО ЖЕ ДЛЯ ВСЕХ ТИПОВ, НА ТОМ ЖЕ ВЫРОВНЕННОМ РАЗМЕРЕ — чтобы «до» и «после» были сравнимы"); print("="*112)
print(f"  {'корпус':>26s} {'все типы':>9s} {'ядра':>7s} {'сдвиг':>8s}")
for lab,T in CORP:
    d,c,dep,P,U=decompose(T)
    if len(c)<NC: continue
    def avg(pool):
        v=[]
        for s in range(25):
            rnd=random.Random(300+s); r=shape_of(rnd.sample(pool,NC))[2]
            if r==r: v.append(r)
        return st.mean(v) if v else float('nan')
    x=avg(list(T)); y=avg(c)
    print(f"  {lab:>26s} {x:9.2f} {y:7.2f} {y-x:+8.2f}")
