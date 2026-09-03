# -*- coding: utf-8 -*-
"""Приписывание даёт длину, но не даёт расхождения. Подмена первого знака
даёт расхождение, но не даёт длины. Берёт ли смесь обе меры сразу.

ПОДГОНКА по двум мерам: прибавка длины и расхождение первого знака.
ОТЛОЖЕНО: доля Гроува, расхождение остатков, слова только-в-началах."""
import json, collections, random, statistics as st, sys
exec(open("scripts/arch_line.py").read().split('V=dict(ldiv=')[0])
VT_MS=set(VOY)

def gen3(p_prep, p_sub, seed=0, wc=40):
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
            if i==0 and PREP:
                r=rnd.random()
                if r<p_prep: x=PREP[rnd.randrange(len(PREP))]+x
                elif r<p_prep+p_sub and len(x)>2: x=PREP[rnd.randrange(len(PREP))]+x[1:]
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
    return dict(ld=st.mean(len(w) for w in FI)-st.mean(len(w) for w in MID),
                div=line_div(L), grove=len(dec)/len(FI), sd=sd)
TG=meas(VL)
print(f"  цель: длина {TG['ld']:+.3f}, расхождение {TG['div']:.3f} | ОТЛОЖЕНО: Гроув {TG['grove']:.3f}, остатки {TG['sd']:.3f}")
print("\n"+"="*100); print("СМЕСЬ ПРИПИСЫВАНИЯ И ПОДМЕНЫ (подгонка по длине и расхождению)"); print("="*100)
print(f"  {'припис.':>8s} {'подмена':>8s} {'длина':>8s} {'доля':>6s} {'расхожд.':>9s} {'доля':>6s} | {'Гроув':>7s} {'доля':>6s} {'остатки':>8s} {'доля':>6s}")
best=None
for pp in [0.2,0.3,0.4,0.5]:
    for ps in [0.0,0.2,0.4,0.6]:
        ds=[meas(gen3(pp,ps,seed=s)) for s in range(2)]
        f=lambda k: st.mean(d[k] for d in ds)
        e=abs(f('ld')-TG['ld'])/TG['ld']+abs(f('div')-TG['div'])/TG['div']
        if best is None or e<best[0]: best=(e,pp,ps,f('ld'),f('div'),f('grove'),f('sd'))
        print(f"  {pp:8.2f} {ps:8.2f} {f('ld'):+8.3f} {f('ld')/TG['ld']:5.0%} {f('div'):9.3f} {f('div')/TG['div']:5.0%} | "
              f"{f('grove'):7.3f} {f('grove')/TG['grove']:5.0%} {f('sd'):8.3f} {f('sd')/TG['sd']:5.0%}")
        sys.stdout.flush()
e,pp,ps,ld,dv,gr,sd=best
print(f"\n  ЛУЧШАЯ ТОЧКА: приписывание {pp}, подмена {ps}")
print(f"    подогнано: длина {ld:+.3f}/{ld/TG['ld']:.0%}, расхождение {dv:.3f}/{dv/TG['div']:.0%}")
print(f"    ОТЛОЖЕНО : Гроув {gr:.3f}/{gr/TG['grove']:.0%}, остатки {sd:.3f}/{sd/TG['sd']:.0%}")
