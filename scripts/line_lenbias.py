# -*- coding: utf-8 -*-
"""Почему длина даёт p≈0,40, а расхождение первого знака p≈0,85.

Гипотеза: оценка по длине СМЕЩЕНА ВНИЗ, потому что тест разложимости
(«снял знак — остался словарь») находит короткие остатки охотнее длинных:
длинное слово реже встречается, значит остаток реже попадает в словарь.
Тогда наблюдаемая прибавка длины меньше настоящей доли приписывания.

Проверка в генераторе, где настоящая доля ИЗВЕСТНА."""
import json, collections, random, statistics as st, sys
exec(open("scripts/arch_line.py").read().split('V=dict(ldiv=')[0])
VT_MS=set(VOY)

def diag(L, T=None):
    T=T or {w for l in L for w in l}
    FI=[l[0] for l in L if l]; MID=[w for l in L for w in l[1:]]
    dec=[w for w in FI if len(w)>2 and w[1:] in T]
    stems=[w[1:] for w in dec]
    return dict(ld=st.mean(len(w) for w in FI)-st.mean(len(w) for w in MID),
                stem_len=st.mean(len(w) for w in stems) if stems else float("nan"),
                mid_len=st.mean(len(w) for w in MID),
                grove=len(dec)/len(FI),
                div=line_div(L))
m=diag(VL, VT_MS)
print("="*96); print("РУКОПИСЬ"); print("="*96)
print(f"  прибавка длины {m['ld']:+.3f} | длина остатка {m['stem_len']:.2f} против серединного слова {m['mid_len']:.2f} "
      f"(короче на {m['mid_len']-m['stem_len']:.2f}) | разложимо {m['grove']:.1%} | расхождение {m['div']:.3f}")
print("\n"+"="*96); print("ГЕНЕРАТОР: настоящая доля известна, смещена ли оценка по длине"); print("="*96)
print(f"  {'настоящее p':>12s} {'прибавка длины':>15s} {'длина остатка':>14s} {'серединное':>11s} {'короче на':>10s} {'разложимо':>10s} {'расхожд.':>9s}")
for p in [0.0,0.2,0.4,0.6,0.8,1.0]:
    ds=[diag(gen_lines(p,seed=s)) for s in range(3)]
    f=lambda k: st.mean(d[k] for d in ds)
    print(f"  {p:12.2f} {f('ld'):+15.3f} {f('stem_len'):14.2f} {f('mid_len'):11.2f} "
          f"{f('mid_len')-f('stem_len'):10.2f} {f('grove'):10.1%} {f('div'):9.3f}")
    sys.stdout.flush()
print("\n  если в генераторе прибавка длины РАВНА настоящему p, оценка не смещена,")
print("  и тогда у рукописи p действительно ≈0,40, а расхождение 0,385 приписыванием НЕ БЕРЁТСЯ")
