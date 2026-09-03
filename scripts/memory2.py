# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, math
exec(open("scripts/memory.py").read().split('print("="*112)')[0])
T=battery(VL,"РУКОПИСЬ")
def fit_err(d):
    """ошибка ТОЛЬКО по трём мерам возврата — остальное не участвует"""
    return (abs(d['r1']-T['r1'])/T['r1'] + abs(d['r2']-T['r2'])/T['r2']
            + abs(d['tail']-T['tail'])/T['tail'])
print("="*112); print("ПОДГОНКА КЕША ПО ПРОФИЛЮ ВОЗВРАТА (четыре правых столбца НЕ участвуют)"); print("="*112)
print(f"  {'p':>5s} {'окно':>6s} {'d1-5':>7s} {'d6-20':>7s} {'выход':>6s} {'ошибка':>8s} | "
      f"{'соседство':>10s} {'автокорр':>9s} {'ранг-корр':>10s} {'стык':>7s}")
print(f"  {'—':>5s} {'—':>6s} {T['r1']:7.2f} {T['r2']:7.2f} {T['tail']:6d} {'ЦЕЛЬ':>8s} | "
      f"{T['adj']:9.2f}× {T['la']:+9.3f} {T['rc']:+10.4f} {T['j']:7.3f}")
res=[]
for p in (0.05,0.10,0.15,0.20,0.30):
    for w in (5,15,40,100,300):
        d=battery(cache(p,w,0), f"p={p} w={w}")
        e=fit_err(d); res.append((e,p,w,d))
res.sort(key=lambda x:x[0])
for e,p,w,d in res[:8]:
    print(f"  {p:5.2f} {w:6d} {d['r1']:7.2f} {d['r2']:7.2f} {d['tail']:6d} {e:8.3f} | "
          f"{d['adj']:9.2f}× {d['la']:+9.3f} {d['rc']:+10.4f} {d['j']:7.3f}")
print("\n  худшие для сравнения:")
for e,p,w,d in res[-3:]:
    print(f"  {p:5.2f} {w:6d} {d['r1']:7.2f} {d['r2']:7.2f} {d['tail']:6d} {e:8.3f} | "
          f"{d['adj']:9.2f}× {d['la']:+9.3f} {d['rc']:+10.4f} {d['j']:7.3f}")
