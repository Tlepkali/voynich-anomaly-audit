# -*- coding: utf-8 -*-
"""Не ломает ли механизм строки четыре прежние подписи."""
import json, collections, random, statistics as st, math
exec(open("scripts/arch_line.py").read().split('V=dict(ldiv=')[0])
T4=battery(VL,"")
def prof(L):
    r=recurrence(L,60); a,b,t=prof_summary(r)
    return dict(r1=a, la=len_autocorr(L), rc=rank_corr(L), j=junc1(L))
print("="*100); print("ЧЕТЫРЕ ПРЕЖНИЕ ПОДПИСИ ПРИ ВКЛЮЧЁННОМ МЕХАНИЗМЕ СТРОКИ"); print("="*100)
print(f"  {'p':>5s} | {'возврат':>10s} {'автокорр':>11s} {'ранг':>11s} {'стык':>11s} {'все 4?':>7s}")
print(f"  {'ЦЕЛЬ':>5s} | {T4['r1']:10.2f} {T4['la']:+11.3f} {T4['rc']:+11.4f} {T4['j']:11.3f}")
for p in (0.0,0.4,0.8):
    ds=[prof(gen_lines(p,seed=s)) for s in range(2)]
    m={k:st.mean(d[k] for d in ds) for k in ("r1","la","rc","j")}
    f=lambda k: m[k]/T4[k]
    ok=all(f(k)>=0.70 for k in ("r1","la","rc","j"))
    print(f"  {p:5.1f} | {m['r1']:7.2f}/{f('r1'):3.0%} {m['la']:+8.3f}/{f('la'):3.0%} "
          f"{m['rc']:+8.4f}/{f('rc'):3.0%} {m['j']:8.3f}/{f('j'):3.0%} {'ДА' if ok else 'нет':>7s}")
print("\n  (в этом прогоне выбор соседа берётся равновероятно, без взвешивания —")
print("   потому стык ниже, чем в разделе 7.6; сравнивать надо строки между собой)")
