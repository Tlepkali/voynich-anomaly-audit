# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys, math
exec(open("scripts/order.py").read().split('CORP=[("Войнич",VOY)]')[0])
NM=12000
def trim(flat,n=NM): return flat[:n]
CORP=[("Войнич",VOY)]
for nm,fn in [("латынь","latin"),("английский","english"),("итальянский","wiki_it")]:
    w=load(fn)
    if w: CORP.append((nm,w))
sys.path.insert(0,"scripts"); sys.path.insert(0,".")
exec(open("scripts/oos.py").read().split("CORP=")[0])
M=model()
if M: CORP.append(("МОДЕЛЬ",[w for l in M for w in l]))
CORP=[(nm,trim(f)) for nm,f in CORP if len(f)>=NM]
LENS=[l for l in LENS]  # cut() уже режет по строкам рукописи
print("="*112); print(f"ВЫРОВНЕННЫЙ ОБЪЁМ {NM} СЛОВ: повторяющиеся биграммы"); print("="*112)
print(f"  {'корпус':>14s} {'набл.':>7s} {'окно 10':>15s} {'окно 50':>15s}")
for nm,f in CORP:
    o,_=rep_bigram(f)
    a=st.mean(rep_bigram(wshuf(f,10,s))[0] for s in range(6))
    b=st.mean(rep_bigram(wshuf(f,50,s))[0] for s in range(6))
    print(f"  {nm:>14s} {o:7.3f} {a:8.3f} ({o/a:4.2f}×) {b:8.3f} ({o/b:4.2f}×)")
print("\n"+"="*112); print("МАССА КОРЗИН ЧАСТОТЫ (нужна, чтобы понять, сравнимы ли MI между корпусами)"); print("="*112)
print(f"  {'корпус':>14s} {'топ-10':>8s} {'11–50':>8s} {'51–200':>8s} {'201–1000':>9s} {'прочие':>8s} {'H(класс)':>9s}")
for nm,f in CORP:
    b=buckets(f); cc=collections.Counter(b[w] for w in f); n=len(f)
    H=-sum(v/n*math.log2(v/n) for v in cc.values())
    print(f"  {nm:>14s} "+" ".join(f"{cc.get(i,0)/n:8.1%}" for i in range(5))+f" {H:9.3f}")
print("\n"+"="*112); print("НОРМИРОВАННАЯ ВЗАИМНАЯ ИНФОРМАЦИЯ КЛАССОВ: MI / H(класс) — снимает разницу масс"); print("="*112)
print(f"  {'корпус':>14s} {'MI':>8s} {'H':>7s} {'MI/H набл.':>11s} {'MI/H окно 10':>14s} {'MI/H окно 50':>14s} {'отношение':>10s}")
for nm,f in CORP:
    b=buckets(f); cc=collections.Counter(b[w] for w in f); n=len(f)
    H=-sum(v/n*math.log2(v/n) for v in cc.values())
    o=class_mi(f,b)
    a=st.mean(class_mi(wshuf(f,10,s),b) for s in range(6))
    d=st.mean(class_mi(wshuf(f,50,s),b) for s in range(6))
    print(f"  {nm:>14s} {o:8.4f} {H:7.3f} {o/H:11.4f} {a/H:14.4f} {d/H:14.4f} {o/max(d,1e-9):9.1f}×")
print("\n"+"="*112); print("ПРЕДСКАЗАНИЕ СЛЕДУЮЩЕГО СЛОВА НА ОТЛОЖЕННОЙ ПОЛОВИНЕ (биграммы учатся на первой)"); print("="*112)
print(f"  {'корпус':>14s} {'пар в тесте':>12s} {'угадано':>9s} {'при окне 50':>13s} {'отношение':>10s}")
def holdout_pred(f,shuf=None,seed=0):
    g=wshuf(f,50,seed) if shuf else f
    L=cut(g); half=len(L)//2
    tr,te=L[:half],L[half:]
    nxt=collections.defaultdict(set)
    for l in tr:
        for i in range(len(l)-1): nxt[l[i]].add(l[i+1])
    hit=tot=0
    for l in te:
        for i in range(len(l)-1):
            tot+=1
            if l[i+1] in nxt.get(l[i],()): hit+=1
    return hit/max(tot,1), tot
for nm,f in CORP:
    o,tot=holdout_pred(f)
    s=st.mean(holdout_pred(f,True,x)[0] for x in range(5))
    print(f"  {nm:>14s} {tot:12d} {o:9.1%} {s:13.1%} {o/max(s,1e-9):9.2f}×")
