# -*- coding: utf-8 -*-
"""Пятый вариант, экономно: три точки, два зерна, кандидаты подвыбираются."""
import json, collections, random, statistics as st, math
exec(open("scripts/construct3.py").read().split('print("="*112)')[0])
BW={k:collections.Counter(v) for k,v in BPOOL.items()}
def pick_w(cands, prev, rnd, cap=60):
    if prev is None or not cands:
        return cands[rnd.randrange(len(cands))] if cands else None
    w=BW.get(prev[-1])
    if not w: return cands[rnd.randrange(len(cands))]
    if len(cands)>cap: cands=[cands[rnd.randrange(len(cands))] for _ in range(cap)]
    f=[(c,w.get(c[0],0)) for c in cands]
    f=[(c,n) for c,n in f if n>0]
    if not f: return None
    tot=sum(n for _,n in f); r=rnd.random()*tot; acc=0
    for c,n in f:
        acc+=n
        if acc>=r: return c
    return f[-1][0]
def arch5(pn,pc,pr,seed=0,wc=40):
    rnd=random.Random(seed); out=[]; prev=None; q=collections.deque(maxlen=wc)
    while len(out)<len(VOY):
        u=rnd.random(); x=None
        if prev is not None and u<pn and NB.get(prev): x=pick_w(NB[prev],prev,rnd)
        elif q and u<pn+pc: x=pick_w(list(q),prev,rnd)
        elif prev is not None and u<pn+pc+pr: x=pick_w(BYCLS.get(CLS.get(prev,0),[]),prev,rnd)
        if x is None: x=build_word(prev,rnd)
        out.append(x); prev=x; q.append(x)
    return cut(out[:len(VOY)])
print("="*100); print("ПЯТЫЙ ВАРИАНТ: память ВЗВЕШЕНА частотой перехода (три точки, два зерна)"); print("="*100)
print(f"  {'сосед':>6s} {'кеш':>5s} {'част':>5s} | {'возврат':>9s} {'автокорр':>10s} {'ранг':>10s} {'СТЫК':>12s} {'все 4?':>7s}")
for pn,pc,pr in [(0.25,0.05,0.10),(0.25,0.05,0.00),(0.15,0.10,0.20)]:
    ds=[battery(arch5(pn,pc,pr,seed=s),"") for s in range(2)]
    m={k:st.mean(d[k] for d in ds) for k in ("r1","la","rc","j")}
    f=lambda k: m[k]/T[k]
    ok=all(f(k)>=0.70 for k in ("r1","la","rc","j"))
    print(f"  {pn:6.2f} {pc:5.2f} {pr:5.2f} | {f('r1'):8.0%} {f('la'):9.0%} {f('rc'):9.0%} {m['j']:7.3f} {f('j'):3.0%} {'ДА' if ok else 'нет':>7s}")
print("\n  МАКСИМУМ СТЫКА при трёх взятых подписях, по архитектурам:")
print("    1. выбор (503 точки решётки)             26 %")
print("    2. гибрид, память игнорирует границу     41 %")
print("    3. память ФИЛЬТРОВАНА по законности      55 %")
print("    4. память ВЗВЕШЕНА частотой перехода     — см. выше")
