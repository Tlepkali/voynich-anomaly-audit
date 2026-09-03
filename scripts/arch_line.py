# -*- coding: utf-8 -*-
"""Пятое семейство: строка. Один минимальный механизм — в начале строки с
вероятностью p приписать знак спереди. Знак берётся из наблюдённого
распределения приписываемых.
ПОДГОНКА по одной мере: расхождение начала строки.
ОТЛОЖЕНО: доля слов Гроува, слова только-в-началах, превышение по знакам,
конец строки, и все четыре прежние подписи."""
import json, collections, random, statistics as st, math
exec(open("scripts/construct5.py").read().split('print("="*100)')[0])
BEST=(0.15,0.10,0.20)
VT=set(VOY)
# какие знаки приписываются: первое слово строки = знак + словарное слово
PRE=collections.Counter()
for l in VL:
    w=l[0]
    if len(w)>2 and w[1:] in VT: PRE[w[0]]+=1
PREP=[c for c,n in PRE.items() for _ in range(n)]
print("наблюдённые приписываемые знаки:", ", ".join(f"{c}·{n}" for c,n in PRE.most_common(8)))
def line_div(L):
    fi=collections.Counter(l[0][0] for l in L if l)
    mid=collections.Counter(w[0] for l in L for w in l[1:])
    a=sum(fi.values()); b=sum(mid.values())
    return sum(abs(fi[c]/a-mid[c]/b) for c in set(fi)|set(mid))/2
def grove_frac(L):
    """доля первых слов строки, раскладывающихся как знак + словарное слово"""
    n=d=0
    T=set(w for l in L for w in l)
    for l in L:
        w=l[0]; n+=1
        if len(w)>2 and w[1:] in T: d+=1
    return d/max(n,1)
def only_initial(L):
    fi=collections.Counter(l[0] for l in L if l)
    mid=collections.Counter(w for l in L for w in l[1:])
    return sum(1 for w in fi if w not in mid)
def mfinal(L):
    """доля слов на конце строки, кончающихся на m, против середины"""
    f=[l[-1] for l in L if l]; m=[w for l in L for w in l[:-1]]
    a=sum(1 for w in f if w.endswith("m"))/max(len(f),1)
    b=sum(1 for w in m if w.endswith("m"))/max(len(m),1)
    return a, (a/b if b else float('nan'))
def gen_lines(p_prep, seed=0, wc=40):
    """порождаем ПО СТРОКАМ: первое слово строки может получить приписку"""
    rnd=random.Random(seed); out=[]; prev=None; q=collections.deque(maxlen=wc)
    pn,pc,pr=BEST
    for ln in LENS:
        row=[]
        for i in range(ln):
            u=rnd.random(); x=None
            if prev is not None and u<pn and NB.get(prev): x=pick_w(NB[prev],prev,rnd)
            if x is None and q and u<pn+pc: x=pick_w(list(q),prev,rnd)
            if x is None and prev is not None and u<pn+pc+pr:
                x=pick_w(BYCLS.get(CLS.get(prev,0),[]),prev,rnd)
            if x is None: x=build_word(prev,rnd)
            if i==0 and rnd.random()<p_prep and PREP:      # ЕДИНСТВЕННЫЙ механизм строки
                x=PREP[rnd.randrange(len(PREP))]+x
            row.append(x); prev=x; q.append(x)
        out.append(row)
    return out
V=dict(ldiv=line_div(VL), grove=grove_frac(VL), only=only_initial(VL), mfin=mfinal(VL)[1])
print(f"\nрукопись: расхождение {V['ldiv']:.3f}, доля Гроува {V['grove']:.1%}, "
      f"только-в-началах {V['only']}, m на конце {V['mfin']:.1f}×")
print("\n"+"="*100); print("ПОДГОНКА ПО ОДНОЙ МЕРЕ, ОСТАЛЬНОЕ ОТЛОЖЕНО"); print("="*100)
print(f"  {'p':>5s} {'расхожд.':>9s} {'доля':>7s} | {'Гроув':>8s} {'доля':>7s} {'только-в-нач':>13s} {'доля':>7s} {'m на конце':>11s}")
print(f"  {'ЦЕЛЬ':>5s} {V['ldiv']:9.3f} {'100%':>7s} | {V['grove']:7.1%} {'100%':>7s} {V['only']:13d} {'100%':>7s} {V['mfin']:10.1f}×")
for p in (0.0,0.2,0.4,0.6,0.8):
    Ls=[gen_lines(p,seed=s) for s in range(2)]
    d=st.mean(line_div(L) for L in Ls); g=st.mean(grove_frac(L) for L in Ls)
    o=st.mean(only_initial(L) for L in Ls); mf=st.mean(mfinal(L)[1] for L in Ls)
    print(f"  {p:5.1f} {d:9.3f} {d/V['ldiv']:6.0%} | {g:7.1%} {g/V['grove']:6.0%} {o:13.0f} {o/V['only']:6.0%} {mf:10.1f}×")
