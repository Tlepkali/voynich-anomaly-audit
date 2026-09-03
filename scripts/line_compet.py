# -*- coding: utf-8 -*-
"""КОНКУРЕНТ смеси: одно приписывание, но знаки берутся из самого выгодного
набора — наблюдённого распределения ПЕРВЫХ ЗНАКОВ начальных слов, а не из
набора, оценённого по разложимым. Если и так расхождение при верной длине
не берётся, подмена нужна."""
import json, collections, random, statistics as st, sys
exec(open("scripts/arch_line.py").read().split('V=dict(ldiv=')[0])
VT_MS=set(VOY)
# самый выгодный для расхождения набор: первые знаки начальных слов как есть
FIRST=[l[0][0] for l in VL if l]
def gen4(p_prep, pool, seed=0, wc=40, p_sub=0.0):
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
            if i==0 and pool:
                r=rnd.random()
                if r<p_prep: x=pool[rnd.randrange(len(pool))]+x
                elif r<p_prep+p_sub and len(x)>2: x=pool[rnd.randrange(len(pool))]+x[1:]
            row.append(x); prev=x; q.append(x)
        out.append(row)
    return out
def meas(L):
    T={w for l in L for w in l}
    FI=[l[0] for l in L if l]; MID=[w for l in L for w in l[1:]]
    dec=[w for w in FI if len(w)>2 and w[1:] in T]
    a=collections.Counter(w[1] for w in dec); b=collections.Counter(w[1] for w in MID if len(w)>2 and w[1:] in T)
    ta,tb=sum(a.values()),sum(b.values())
    sd=sum(abs(a[c]/ta-b[c]/tb) for c in set(a)|set(b))/2 if ta>100 and tb>100 else float("nan")
    return (st.mean(len(w) for w in FI)-st.mean(len(w) for w in MID), line_div(L), len(dec)/len(FI), sd)
TG=meas(VL)
print(f"  цель: длина {TG[0]:+.3f}, расхождение {TG[1]:.3f} | отложено Гроув {TG[2]:.3f}, остатки {TG[3]:.3f}\n")
print("="*100); print("ТРИ СЕМЕЙСТВА, 3 ЗЕРНА"); print("="*100)
print(f"  {'семейство':>44s} {'длина':>13s} {'расхождение':>17s}")
FAM=[("приписывание, набор по разложимым", PREP, 0.0),
     ("приписывание, набор ВЫГОДНЫЙ (первые знаки)", FIRST, 0.0),
     ("приписывание 0,4 + ПОДМЕНА 0,6", PREP, 0.6)]
for nm,pool,ps in FAM:
    bl=None
    for p in ([0.3,0.4,0.5] if ps>0 else [0.2,0.3,0.4,0.5,0.6,0.8]):
        ds=[meas(gen4(p,pool,seed=s,p_sub=ps)) for s in range(3)]
        ld=st.mean(d[0] for d in ds); dv=st.mean(d[1] for d in ds)
        if bl is None or abs(ld-TG[0])<abs(bl[1]-TG[0]): bl=(p,ld,dv,ds)
    p,ld,dv,ds=bl
    gr=st.mean(d[2] for d in ds); sd=st.mean(d[3] for d in ds)
    print(f"  {nm:>44s} {ld:+8.3f}/{ld/TG[0]:3.0%} {dv:11.3f}/{dv/TG[1]:3.0%}")
    print(f"  {'(при доле '+str(p)+', отложенное)':>44s} {'Гроув '+f'{gr/TG[2]:.0%}':>13s} {'остатки '+f'{sd/TG[3]:.0%}':>17s}")
    sys.stdout.flush()
print("\n  сравнивать по РАСХОЖДЕНИЮ при длине около 100 %: подмена нужна, если")
print("  выгодный набор знаков сам по себе расхождения не даёт")
