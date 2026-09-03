# -*- coding: utf-8 -*-
"""ПОРОЖДЕНИЕМ: два механизма начала строки против одного.

Разбор показал, что начало строки — ДВЕ операции: знак приписывается (доля по
длине ≈0,40) И слово берётся из другой части словаря (расхождение остатков
0,271 при нуле 0,053, p=0,005, шесть транскрипций 0,271–0,287).

ЗАЯВЛЕНО ДО ЗАПУСКА. Если это верно, то семейство с ДВУМЯ рычагами (p — доля
приписывания, b — доля выбора начального слова по строчному распределению)
должно брать все три меры начала строки лучше, чем семейство с одним (b=0).
Мера без порога, как принято в проекте после G18: ЛУЧШАЯ ХУДШАЯ из трёх долей.
Меры берутся ИСПРАВЛЕННЫЕ (доля Гроува по словарю рукописи, только-в-началах
как ДОЛЯ, а не счёт) — сырые завышены побочными следствиями приписывания.
"""
import json, collections, random, statistics as st, math, sys
exec(open("scripts/arch_line.py").read().split('V=dict(ldiv=')[0])

VT_MS=set(VOY)
# распределение первого знака ОСТАТКА начального слова — вторая операция
SPOOL=[]
for l in VL:
    w=l[0]
    if len(w)>2 and w[1:] in VT_MS: SPOOL.append(w[1])
print(f"первый знак остатка начального слова: " +
      ", ".join(f"{c}·{n}" for c,n in collections.Counter(SPOOL).most_common(6)))

def build_word2(prev, rnd, force_c0=None, maxlen=25):
    if force_c0 is not None: c0=force_c0
    elif prev is not None and BPOOL.get(prev[-1]):
        p=BPOOL[prev[-1]]; c0=p[rnd.randrange(len(p))]
    else: c0=FPOOL[rnd.randrange(len(FPOOL))]
    w=c0; ctx=("^"*ORD+c0)[-ORD:]
    while True:
        p=POOLS.get(ctx)
        if not p: break
        ch=p[rnd.randrange(len(p))]
        if ch=="$": break
        w+=ch; ctx=(ctx+ch)[-ORD:]
        if len(w)>=maxlen: break
    return w

def gen2(p_prep, b_sel, seed=0, wc=40):
    rnd=random.Random(seed); out=[]; prev=None; q=collections.deque(maxlen=wc)
    pn,pc,pr=BEST
    for ln in LENS:
        row=[]
        for i in range(ln):
            u=rnd.random(); x=None
            if i==0 and b_sel>0 and rnd.random()<b_sel:
                x=build_word2(prev,rnd,force_c0=SPOOL[rnd.randrange(len(SPOOL))])
            else:
                if prev is not None and u<pn and NB.get(prev): x=pick_w(NB[prev],prev,rnd)
                if x is None and q and u<pn+pc: x=pick_w(list(q),prev,rnd)
                if x is None and prev is not None and u<pn+pc+pr:
                    x=pick_w(BYCLS.get(CLS.get(prev,0),[]),prev,rnd)
                if x is None: x=build_word2(prev,rnd)
            if i==0 and rnd.random()<p_prep and PREP:
                x=PREP[rnd.randrange(len(PREP))]+x
            row.append(x); prev=x; q.append(x)
        out.append(row)
    return out

def grove_fixed(L):
    n=d=0
    for l in L:
        w=l[0]; n+=1
        if len(w)>2 and w[1:] in VT_MS: d+=1
    return d/max(n,1)
def only_rate(L):
    fi=collections.Counter(l[0] for l in L if l)
    mid=collections.Counter(w for l in L for w in l[1:])
    return sum(1 for w in fi if w not in mid)/max(len(fi),1)
MEAS=[("расхожд.",line_div),("Гроув",grove_fixed),("только-в-нач",only_rate)]
TGT={nm:fn(VL) for nm,fn in MEAS}
print("цель:", ", ".join(f"{nm} {v:.3f}" for nm,v in TGT.items()))

def worst(L):
    return min(min(fn(L)/TGT[nm], TGT[nm]/fn(L)) if fn(L)>0 else 0 for nm,fn in MEAS)

GRID_P=[0.0,0.2,0.4,0.6,0.8,1.0]
GRID_B=[0.0,0.2,0.4,0.6,0.8]
print("\n"+"="*100); print("ЛУЧШАЯ ХУДШАЯ ИЗ ТРЁХ ДОЛЕЙ, по решётке (2 зерна)"); print("="*100)
print("     p\\b " + " ".join(f"{b:>8.1f}" for b in GRID_B))
res={}
for p in GRID_P:
    row=[]
    for b in GRID_B:
        Ls=[gen2(p,b,seed=s) for s in range(2)]
        v=st.mean(worst(L) for L in Ls); res[(p,b)]=v; row.append(v)
    print(f"  {p:6.1f} " + " ".join(f"{v:8.0%}" for v in row))
    sys.stdout.flush()
one=max(v for (p,b),v in res.items() if b==0.0)
two=max(res.values())
bp,bb=max(res, key=res.get)
print(f"\n  ОДИН механизм (b=0)  : лучшая худшая доля {one:.0%}")
print(f"  ДВА механизма        : лучшая худшая доля {two:.0%}  при p={bp}, b={bb}")
print("\n  в лучшей точке двух механизмов, по мерам:")
Ls=[gen2(bp,bb,seed=s) for s in range(3)]
for nm,fn in MEAS:
    m=st.mean(fn(L) for L in Ls)
    print(f"    {nm:>14s} {m:8.3f} против цели {TGT[nm]:8.3f}   {m/TGT[nm]:5.0%}")
print("\n  для сравнения, лучшая точка ОДНОГО механизма:")
bp1=max((p for p in GRID_P), key=lambda p: res[(p,0.0)])
Ls=[gen2(bp1,0.0,seed=s) for s in range(3)]
for nm,fn in MEAS:
    m=st.mean(fn(L) for L in Ls)
    print(f"    {nm:>14s} {m:8.3f} против цели {TGT[nm]:8.3f}   {m/TGT[nm]:5.0%}")

# ── СЛЕПЫ ЛИ ТРИ МЕРЫ К ВЫБОРУ СЛОВА ────────────────────────────────────────
print("\n"+"="*100); print("МЕРА, ЧУВСТВИТЕЛЬНАЯ К ВЫБОРУ СЛОВА: расхождение ОСТАТКОВ"); print("="*100)
def stem_div(L):
    T={w for l in L for w in l}
    FI=[l[0] for l in L if l]; MID=[w for l in L for w in l[1:]]
    a=collections.Counter(w[1] for w in FI if len(w)>2 and w[1:] in T)
    b=collections.Counter(w[1] for w in MID if len(w)>2 and w[1:] in T)
    ta,tb=sum(a.values()),sum(b.values())
    if ta<100 or tb<100: return float("nan")
    return sum(abs(a[c]/ta-b[c]/tb) for c in set(a)|set(b))/2
TGT_SD=stem_div(VL)
print(f"  цель (рукопись): {TGT_SD:.3f}; нуль (перемешивание внутри страницы): 0,053")
print(f"\n     p\\b " + " ".join(f"{b:>8.1f}" for b in GRID_B))
for p in GRID_P:
    row=[]
    for b in GRID_B:
        Ls=[gen2(p,b,seed=s) for s in range(2)]
        row.append(st.mean(stem_div(L) for L in Ls))
    print(f"  {p:6.1f} " + " ".join(f"{v:8.3f}" for v in row))
    sys.stdout.flush()
print("\n  если столбец b=0 держится у нуля, а с ростом b растёт к 0,27 —")
print("  вторая операция нужна, а три прежние меры к ней просто СЛЕПЫ")
