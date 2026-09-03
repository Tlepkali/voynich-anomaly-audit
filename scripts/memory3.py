# -*- coding: utf-8 -*-
"""Две памяти вместо одной.
НОВОЕ РАЗДЕЛЕНИЕ, ОБЪЯВЛЕНО ДО ЗАПУСКА:
  подгоняется — профиль возврата (3 числа) И автокорреляция длины;
  отложено — ранг-корреляция соседей и стык по 1 знаку.
"""
import json, collections, random, statistics as st, math
exec(open("scripts/memory.py").read().split('print("="*112)')[0])
T=battery(VL,"РУКОПИСЬ")
def cache2(pl, wl, ps, ws, seed=0):
    """длинная память (тема) + короткая (локальная)"""
    rnd=random.Random(seed); bag=VOY[:]; rnd.shuffle(bag)
    out=[]; longq=collections.deque(maxlen=wl); shortq=collections.deque(maxlen=ws); i=0
    while len(out)<len(VOY) and i<len(bag):
        u=rnd.random()
        if shortq and u<ps: x=shortq[rnd.randrange(len(shortq))]
        elif longq and u<ps+pl: x=longq[rnd.randrange(len(longq))]
        else: x=bag[i]; i+=1
        out.append(x); longq.append(x); shortq.append(x)
    return cut(out[:len(VOY)])
def err(d):
    return (abs(d['r1']-T['r1'])/T['r1'] + abs(d['r2']-T['r2'])/T['r2']
            + abs(d['tail']-T['tail'])/T['tail'] + abs(d['la']-T['la'])/abs(T['la']))
print("="*114); print("ДВЕ ПАМЯТИ: длинная (тема) + короткая (локальная)"); print("="*114)
print(f"  {'p_дл':>5s} {'w_дл':>5s} {'p_кор':>6s} {'w_кор':>6s} {'d1-5':>6s} {'d6-20':>6s} {'вых':>5s} "
      f"{'автокорр':>9s} {'ошибка':>7s} | {'РАНГ-КОРР':>10s} {'СТЫК':>7s} {'соседство':>10s}")
print(f"  {'—':>5s} {'—':>5s} {'—':>6s} {'—':>6s} {T['r1']:6.2f} {T['r2']:6.2f} {T['tail']:5d} "
      f"{T['la']:+9.3f} {'ЦЕЛЬ':>7s} | {T['rc']:+10.4f} {T['j']:7.3f} {T['adj']:9.2f}×")
res=[]
for pl in (0.10,0.15,0.20):
    for wl in (40,100):
        for ps in (0.02,0.05,0.10):
            for ws in (2,4,8):
                d=battery(cache2(pl,wl,ps,ws,0), "")
                res.append((err(d),pl,wl,ps,ws,d))
res.sort(key=lambda x:x[0])
for e,pl,wl,ps,ws,d in res[:7]:
    print(f"  {pl:5.2f} {wl:5d} {ps:6.2f} {ws:6d} {d['r1']:6.2f} {d['r2']:6.2f} {d['tail']:5d} "
          f"{d['la']:+9.3f} {e:7.3f} | {d['rc']:+10.4f} {d['j']:7.3f} {d['adj']:9.2f}×")
print("\n  ОТЛОЖЕННЫЕ (ранг-корреляция и стык) под подгонку НЕ попадали.")
