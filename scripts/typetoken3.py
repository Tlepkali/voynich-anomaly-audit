# -*- coding: utf-8 -*-
import json, collections, math, random, statistics as st
exec(open("scripts/typetoken2.py").read().split('print("="*104)')[0])
NAMES=[("ZL3b-n","Зандб.–Ландини"),("IT2a-n","Такахаси"),("RF1b-e","RF1b-e"),
       ("GC2a-n","Класton v101"),("FG2a-n","FSG"),("CD2a-n","Карриер")]
print("="*112); print("ПО ШЕСТИ ТРАНСКРИПЦИЯМ (латынь нарезана под длины строк каждой)"); print("="*112)
print(f"  {'транскрипция':>16s} {'дл':>3s} | {'ТОКЕНЫ разрыв':>14s} {'ТИПЫ разрыв':>12s} {'токены/типы':>12s} | {'h2 токены':>10s} {'h2 типы':>9s}")
for code,lab in NAMES:
    V=load(code); Ls=[len(l) for l in V]
    w=open("ref/latin.clean").read().split(); LA=[];p=0
    for n in Ls:
        if p+n>len(w): break
        LA.append(w[p:p+n]); p+=n
    tv=[x for l in V for x in l]; tl=[x for l in LA for x in l]
    yv=sorted(set(tv)); yl=sorted(set(tl))
    ml=st.mean(len(x) for x in tv)
    n=4 if ml>4.6 else 3          # у слитных алфавитов слова короче — берём сопоставимую долю
    ev,_=excess(tv,n); el,_=excess(tl,n); pv,_=excess(yv,n); pl,_=excess(yl,n)
    hv,hl=h2_at(tv,n),h2_at(tl,n); qv,ql=h2_at(yv,n),h2_at(yl,n)
    if any(x!=x for x in (ev,el,pv,pl)): print(f"  {lab:>16s} {n:3d} | выборки мало"); continue
    gt,gy=ev/el,pv/pl
    print(f"  {lab:>16s} {n:3d} | {gt:13.2f}× {gy:11.2f}× {gt/gy:11.2f}× | {hv/hl:9.2f}× {qv/ql:8.2f}×")
print("\n  для каждой транскрипции длина выбрана по её средней (4 для EVA, 3 для слитных)")
print("\n"+"="*112); print("ДОВЕРИТЕЛЬНЫЕ ИНТЕРВАЛЫ, которых у раздела не было (бутстрап по словам, 200)"); print("="*112)
V=load("ZL3b-n"); Ls=[len(l) for l in V]
w=open("ref/latin.clean").read().split(); LA=[];p=0
for n in Ls:
    if p+n>len(w): break
    LA.append(w[p:p+n]); p+=n
tv=[x for l in V for x in l]; tl=[x for l in LA for x in l]
yv=sorted(set(tv)); yl=sorted(set(tl))
print(f"  {'мера':>34s} {'отношение В./лат.':>18s} {'95 % ДИ':>18s}")
for lab,a,b,fn,n in [("слотовость, ТОКЕНЫ, длина 4",tv,tl,lambda s,k: mi_at(s,k)[0],4),
                     ("слотовость, ТИПЫ, длина 4",yv,yl,lambda s,k: mi_at(s,k)[0],4),
                     ("h2, ТОКЕНЫ, длина 4",tv,tl,h2_at,4),
                     ("h2, ТИПЫ, длина 4",yv,yl,h2_at,4)]:
    r=boot_ratio(a,b,n,fn)
    if r: print(f"  {lab:>34s} {r[0]:18.2f} [{r[1]:6.2f}; {r[2]:6.2f}]")
