# -*- coding: utf-8 -*-
"""Память над СВОЙСТВАМИ слова, а не над его тождеством.
РАЗДЕЛЕНИЕ ОБЪЯВЛЕНО ДО ЗАПУСКА:
  подгоняется — автокорреляция длины (одна мера);
  отложено — ранг-корреляция соседей, стык по 1 знаку, профиль возврата.
Вопрос: если задать зависимость только по ДЛИНЕ, придут ли остальные сами.
"""
import json, collections, random, statistics as st, math
exec(open("scripts/memory.py").read().split('print("="*112)')[0])
T=battery(VL,"РУКОПИСЬ")
BYLEN=collections.defaultdict(list)
for w in VOY: BYLEN[len(w)].append(w)
LENDIST=collections.Counter(len(w) for w in VOY)
def markov_len(alpha, seed=0):
    """следующее слово берётся из класса длины, притянутого к длине предыдущего:
    с вероятностью alpha длина повторяет предыдущую (±1), иначе из общего распределения"""
    rnd=random.Random(seed)
    lens=[l for l,c in LENDIST.items() for _ in range(c)]
    out=[]; prev=None
    for _ in range(len(VOY)):
        if prev is not None and rnd.random()<alpha:
            cand=[prev-1,prev,prev+1]
            cand=[c for c in cand if c in BYLEN]
            L=cand[rnd.randrange(len(cand))]
        else:
            L=lens[rnd.randrange(len(lens))]
        pool=BYLEN[L]; out.append(pool[rnd.randrange(len(pool))]); prev=L
    return cut(out)
def markov_rank(alpha, nb=6, seed=0):
    """то же, но по КЛАССУ ЧАСТОТЫ: следующее слово из того же класса с вер. alpha"""
    rnd=random.Random(seed)
    c=collections.Counter(VOY); order=[w for w,_ in c.most_common()]
    cls={}; step=max(1,len(order)//nb)
    for i,w in enumerate(order): cls[w]=min(i//step, nb-1)
    byc=collections.defaultdict(list)
    for w in VOY: byc[cls[w]].append(w)
    allw=VOY[:]
    out=[]; prev=None
    for _ in range(len(VOY)):
        if prev is not None and rnd.random()<alpha and byc[prev]:
            x=byc[prev][rnd.randrange(len(byc[prev]))]
        else:
            x=allw[rnd.randrange(len(allw))]
        out.append(x); prev=cls[x]
    return cut(out)
print("="*112); print("ПАМЯТЬ НАД СВОЙСТВАМИ: подгонка ТОЛЬКО по автокорреляции длины"); print("="*112)
print(f"  {'модель':>28s} {'автокорр':>9s} {'ошибка':>8s} | {'РАНГ-КОРР':>10s} {'СТЫК':>7s} {'возв d1-5':>10s} {'соседство':>10s}")
print(f"  {'РУКОПИСЬ':>28s} {T['la']:+9.3f} {'ЦЕЛЬ':>8s} | {T['rc']:+10.4f} {T['j']:7.3f} {T['r1']:10.2f} {T['adj']:9.2f}×")
best=None
for a in (0.1,0.2,0.3,0.4,0.5,0.6):
    d=battery(markov_len(a,0), f"по длине, a={a}")
    e=abs(d['la']-T['la'])/abs(T['la'])
    print(f"  {d['lab']:>28s} {d['la']:+9.3f} {e:8.3f} | {d['rc']:+10.4f} {d['j']:7.3f} {d['r1']:10.2f} {d['adj']:9.2f}×")
    if best is None or e<best[0]: best=(e,a,d)
print()
for a in (0.2,0.4,0.6):
    d=battery(markov_rank(a,6,0), f"по классу частоты, a={a}")
    print(f"  {d['lab']:>28s} {d['la']:+9.3f} {'—':>8s} | {d['rc']:+10.4f} {d['j']:7.3f} {d['r1']:10.2f} {d['adj']:9.2f}×")
print("\n  ОТЛОЖЕННЫЕ: ранг-корреляция, стык, возврат — под подгонку не попадали.")
