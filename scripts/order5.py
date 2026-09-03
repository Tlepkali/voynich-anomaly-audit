# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys, math
exec(open("scripts/order4.py").read().split('print("="*110); print("ПОВТОРЯЮЩИЕСЯ')[0])
exec(open("scripts/coretext.py").read().split("root,frac=build_map")[0])
S=set(VOY); rV,fV=build_map(S,15); CV=[[rV.get(w,w) for w in l] for l in VL]
lw=open("ref/latin.clean").read().split(); LL=[];p=0
for l in VL:
    if p+len(l)>len(lw): break
    LL.append(lw[p:p+len(l)]); p+=len(l)
SL=set(w for l in LL for w in l); rL,fL=build_map(SL,400); CL=[[rL.get(w,w) for w in l] for l in LL]
print("="*104); print("СРАВНЕНИЕ КАК С КАК: рукопись и латынь, обе в исходном виде и обе в ядрах"); print("="*104)
print(f"  {'текст':>32s} {'выведено':>9s} {'r(все пары)':>12s} {'r(без соседей ≤1)':>18s}")
for lab,L,fr in [("Войнич, исходный",VL,0.0),(f"Войнич В ЯДРАХ",CV,fV),
                 ("латынь, исходная",LL,0.0),(f"латынь В ЯДРАХ",CL,fL)]:
    f=[w for l in L for w in l]
    a,_=rankcorr(f); c,_=rankcorr(f,drop=near)
    fs=f"{fr:.0%}" if fr else "—"
    print(f"  {lab:>32s} {fs:>9s} {a:12.4f} {c:18.4f}")
print("\n"+"="*104); print("ДОВЕРИТЕЛЬНЫЕ ИНТЕРВАЛЫ (бутстрап ПО СТРОКАМ, 400 повторов)"); print("="*104)
def boot(L,drop=None,B=400):
    rnd=random.Random(77); out=[]
    for _ in range(B):
        s=[L[rnd.randrange(len(L))] for _ in range(len(L))]
        f=[w for l in s for w in l]
        r,_=rankcorr(f,drop=drop)
        if r==r: out.append(r)
    out.sort(); return st.mean(out), out[int(.025*len(out))], out[int(.975*len(out))]
print(f"  {'текст':>32s} {'r':>9s} {'95 % ДИ':>18s}   (пары без соседей на расстоянии ≤1)")
for lab,L in [("Войнич, исходный",VL),("Войнич в ядрах",CV),("латынь, исходная",LL),("латынь в ядрах",CL)]:
    m,lo,hi=boot(L,drop=near)
    print(f"  {lab:>32s} {m:9.4f} [{lo:+7.4f}; {hi:+7.4f}]")
