# -*- coding: utf-8 -*-
"""Пятый вариант: память не просто фильтруется по законности, а взвешивается
наблюдённой частотой перехода P(первый знак | последний знак предыдущего).
Проверяет объяснение: стыку нужны ЧАСТОТЫ переходов, а не только их носитель."""
import json, collections, random, statistics as st, math
exec(open("scripts/construct3.py").read().split('print("="*112)')[0])
BW={k:collections.Counter(v) for k,v in BPOOL.items()}   # частоты первых знаков
def pick_w(cands, prev, rnd):
    """выбор среди кандидатов ВЗВЕШЕННЫЙ частотой перехода"""
    if prev is None:
        return cands[rnd.randrange(len(cands))] if cands else None
    w=BW.get(prev[-1])
    if not w: return cands[rnd.randrange(len(cands))] if cands else None
    f=[(c, w.get(c[0],0)) for c in cands]
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
        if prev is not None and u<pn and NB.get(prev): x=pick_w(NB[prev], prev, rnd)
        elif q and u<pn+pc: x=pick_w(list(q), prev, rnd)
        elif prev is not None and u<pn+pc+pr: x=pick_w(BYCLS.get(CLS.get(prev,0),[]), prev, rnd)
        if x is None: x=build_word(prev, rnd)
        out.append(x); prev=x; q.append(x)
    return cut(out[:len(VOY)])
def multi5(args,seeds=3):
    ds=[battery(arch5(*args,seed=s),"") for s in range(seeds)]
    return {k:(st.mean(d[k] for d in ds), st.stdev(d[k] for d in ds) if len(ds)>1 else 0) for k in ("r1","r2","la","rc","j")}
def err(m):
    return sum(abs(m[k][0]-T[k])/abs(T[k]) for k in ("r1","r2","la","rc"))
print("="*104); print("ПЯТЫЙ ВАРИАНТ: память ВЗВЕШЕНА частотой перехода, а не просто фильтрована"); print("="*104)
print(f"  {'сосед':>6s} {'кеш':>5s} {'част':>5s} | {'возврат':>9s} {'автокорр':>10s} {'ранг':>10s} | {'СТЫК':>10s} {'взято 4?':>9s}")
print(f"  {'ЦЕЛЬ':>6s} {'':>5s} {'':>5s} | {T['r1']:9.2f} {T['la']:+10.3f} {T['rc']:+10.4f} | {T['j']:10.3f}")
res=[]
for pn in (0.15,0.25,0.35):
    for pc in (0.05,0.10,0.20):
        for pr in (0.0,0.10,0.20):
            m=multi5((pn,pc,pr)); res.append((err(m),pn,pc,pr,m))
res.sort(key=lambda x:x[0])
allfour=0
for e,pn,pc,pr,m in res[:8]:
    f=lambda k: m[k][0]/T[k]
    ok=all(f(k)>=0.70 for k in ("r1","la","rc","j"))
    print(f"  {pn:6.2f} {pc:5.2f} {pr:5.2f} | {f('r1'):8.0%} {f('la'):9.0%} {f('rc'):9.0%} | {m['j'][0]:7.3f} {f('j'):3.0%} {'ДА' if ok else 'нет':>8s}")
allfour=sum(1 for e,pn,pc,pr,m in res if all(m[k][0]/T[k]>=0.70 for k in ("r1","la","rc","j")))
print(f"\n  точек, взявших ВСЕ ЧЕТЫРЕ: {allfour} из {len(res)}")
print("\n  для сравнения максимум стыка при трёх взятых:")
print("    выбор (503 точки решётки)          26 %")
print("    гибрид, память игнорирует границу  41 %")
print("    память ФИЛЬТРОВАНА по законности   55 %")
mj=max((m['j'][0]/T['j'] for e,pn,pc,pr,m in res if sum(1 for k in ("r1","la","rc") if m[k][0]/T[k]>=0.70)>=2), default=0)
print(f"    память ВЗВЕШЕНА частотой           {mj:.0%}")
