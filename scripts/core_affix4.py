# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys
exec(open("scripts/core_affix.py").read().split("CORP=[")[0])
NC=1800
def shape_of(T):
    T=set(T); nb=nbrs(T)
    def m(d):
        g=[len(nb.get(w,())) for w in T if len(w)==d]
        return st.mean(g) if len(g)>=12 else float('nan')
    a,b=m(3),m(5)
    return (b/a if a==a and b==b and a>0 else float('nan'))
def avg_shape(pool,reps=12,seed=400):
    v=[]
    pool=list(pool)
    if len(pool)<NC: return float('nan')
    for s in range(reps):
        r=shape_of(random.Random(seed+s).sample(pool,NC))
        if r==r: v.append(r)
    return st.mean(v) if v else float('nan')
T=topN(VOY); d,cores,dep,P,U=decompose(T); k=len(d)
nb=nbrs(set(T))
base=avg_shape(T,seed=1000); real=avg_shape(cores,seed=1000)
print("="*100); print("КОНТРОЛЬ 3, ИСПРАВЛЕННЫЙ: удаление, взвешенное по числу соседей (максимум механики)"); print("="*100)
print(f"  все типы  {base:.2f}   ядра {real:.2f}   сдвиг {real-base:+.2f}   (тот же посев для всех строк)")
w=[len(nb.get(x,()))+0.5 for x in T]
vals=[]
for s in range(10):
    rnd=random.Random(1100+s)
    drop=set()
    pool=list(T); ww=w[:]
    while len(drop)<k and pool:
        i=rnd.choices(range(len(pool)),weights=ww,k=1)[0]
        drop.add(pool[i]); pool.pop(i); ww.pop(i)
    r=avg_shape([x for x in T if x not in drop],reps=6,seed=1200+s*7)
    if r==r: vals.append(r)
if vals:
    print(f"  удалено {k} типов с вероятностью ∝ числу соседей: {st.mean(vals):.2f} "
          f"(разброс {min(vals):.2f}–{max(vals):.2f})  сдвиг {st.mean(vals)-base:+.2f}")
print("\n"+"="*100); print("СВОДКА ПО ЗАЩИТАМ (все сдвиги от одной базы, один посев)"); print("="*100)
print(f"  {'что сделано':>56s} {'дл5/дл3':>9s} {'сдвиг':>8s}")
print(f"  {'ничего (все 5000 типов)':>56s} {base:9.2f} {0.0:+8.2f}")
print(f"  {'снят настоящий обвес → 2049 ядер':>56s} {real:9.2f} {real-base:+8.2f}")
if vals: print(f"  {'удалено столько же, взвешенно по соседям':>56s} {st.mean(vals):9.2f} {st.mean(vals)-base:+8.2f}")
