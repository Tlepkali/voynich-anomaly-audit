# -*- coding: utf-8 -*-
"""Возражение ololololo: не подогнано ли всё под числа рукописи.
Честная форма — решётка по ВСЕМ четырём долям без подгонки: есть ли хоть одна
точка, берущая все четыре подписи. Порог «взято» = 70 % цели."""
import json, collections, random, statistics as st, math
exec(open("scripts/memory7.py").read().split('print(f"типов')[0])
TYPES=sorted(set(VOY)); NB=nbr_map(TYPES)
c=collections.Counter(VOY); order=[w for w,_ in c.most_common()]
NBC=6; step=max(1,len(order)//NBC)
CLS={w:min(i//step,NBC-1) for i,w in enumerate(order)}
BYCLS=collections.defaultdict(list)
for w in VOY: BYCLS[CLS[w]].append(w)
BYFIRST=collections.defaultdict(list)
for w in VOY: BYFIRST[w[0]].append(w)
TRANS=collections.defaultdict(collections.Counter)
for l in VL:
    for a,b in zip(l,l[1:]): TRANS[a[-1]][b[0]]+=1
POOLS={k:[ch for ch,n in v.items() for _ in range(n)] for k,v in TRANS.items()}
def gen(pn,pc,pr,pb,seed=0,wc=40):
    rnd=random.Random(seed); bag=VOY[:]; rnd.shuffle(bag)
    out=[]; prev=None; q=collections.deque(maxlen=wc); i=0
    while len(out)<len(VOY) and i<len(bag):
        u=rnd.random(); x=None
        if prev is not None and u<pb and POOLS.get(prev[-1]):
            pl=POOLS[prev[-1]]; ch=pl[rnd.randrange(len(pl))]
            p2=BYFIRST.get(ch)
            if p2: x=p2[rnd.randrange(len(p2))]
        if x is None and prev is not None and u<pb+pn and NB.get(prev):
            n=NB[prev]; x=n[rnd.randrange(len(n))]
        if x is None and q and u<pb+pn+pc: x=q[rnd.randrange(len(q))]
        if x is None and prev is not None and u<pb+pn+pc+pr:
            b=BYCLS[CLS[prev]]; x=b[rnd.randrange(len(b))]
        if x is None: x=bag[i]; i+=1
        out.append(x); prev=x; q.append(x)
    return cut(out[:len(VOY)])
T=battery(VL,"")
def four(L):
    r=recurrence(L,60); a,b,t=prof_summary(r)
    return dict(r1=a, la=len_autocorr(L), rc=rank_corr(L), j=junc1(L))
def frac(d):
    return dict(r1=d['r1']/T['r1'], la=d['la']/T['la'], rc=d['rc']/T['rc'], j=d['j']/T['j'])
GRID=[0.0,0.1,0.2,0.3,0.4]
pts=[(pn,pc,pr,pb) for pn in GRID for pc in GRID for pr in GRID for pb in GRID if pn+pc+pr+pb<=1.0]
print(f"точек решётки: {len(pts)} (сумма долей ≤ 1), одно зерно на точку")
THR=0.70
best4=[]; cnt=collections.Counter()
for p in pts:
    f=frac(four(gen(*p,seed=0)))
    k=sum(1 for v in f.values() if v>=THR)
    cnt[k]+=1
    if k>=3: best4.append((k,p,f))
print("\n"+"="*100); print(f"СКОЛЬКО ПОДПИСЕЙ ВЗЯТО (порог {THR:.0%} цели)"); print("="*100)
for k in sorted(cnt, reverse=True):
    print(f"  {k} из 4: {cnt[k]:4d} точек" + ("   ← ни одной" if k==4 and cnt[k]==0 else ""))
print(f"\n  точек, взявших ВСЕ ЧЕТЫРЕ: {cnt.get(4,0)}")
best4.sort(key=lambda x:-(x[0]+min(x[2].values())))
print("\n"+"="*100); print("ЛУЧШИЕ ТОЧКИ (по числу взятых и по худшей из четырёх)"); print("="*100)
print(f"  {'сосед':>6s} {'кеш':>5s} {'част':>5s} {'гран':>5s} | {'возврат':>8s} {'автокорр':>9s} {'ранг':>7s} {'СТЫК':>7s} {'взято':>6s}")
for k,p,f in best4[:10]:
    print(f"  {p[0]:6.1f} {p[1]:5.1f} {p[2]:5.1f} {p[3]:5.1f} | {f['r1']:7.0%} {f['la']:8.0%} {f['rc']:6.0%} {f['j']:6.0%} {k:5d}/4")
mj=max(f['j'] for _,_,f in best4) if best4 else 0
allj=[frac(four(gen(*p,seed=0)))['j'] for p in pts[:0]]
print(f"\n  максимум стыка среди точек, взявших ≥3 других: {mj:.0%}")
