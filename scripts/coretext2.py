# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys, math
exec(open("scripts/coretext.py").read().split("root,frac=build_map")[0])
S=set(VOY)
print("="*120); print("ВЫРАВНИВАНИЕ ДОЛИ ВЫВОДА: у латыни потолок 33 %, значит опускаем рукопись до неё"); print("="*120)
cand=[]
for k in (1,2,3,4,5,6,8,10,15):
    r,f=build_map(S,k); cand.append((abs(f-0.33),k,f,r))
cand.sort(); _,kV,fV,rootV=cand[0]
print(f"  рукопись: k={kV} даёт {fV:.0%} выведенных типов (цель 33 %)")
lw=open("ref/latin.clean").read().split()
LL=[];p=0
for l in VL:
    if p+len(l)>len(lw): break
    LL.append(lw[p:p+len(l)]); p+=len(l)
SL=set(w for l in LL for w in l)
c2=[]
for k in (100,170,260,400,600):
    r,f=build_map(SL,k); c2.append((abs(f-0.33),k,f,r))
c2.sort(); _,kL,fL,rootL=c2[0]
print(f"  латынь  : k={kL} даёт {fL:.0%}")
def tokfrac(lines,root): 
    f=[w for l in lines for w in l]; return sum(1 for w in f if root.get(w,w)!=w)/len(f)
print(f"  переписано ТОКЕНОВ: рукопись {tokfrac(VL,rootV):.0%}, латынь {tokfrac(LL,rootL):.0%}")
rows=[batt(VL,"Войнич, как есть"), batt(rewrite(VL,rootV),f"Войнич в ядрах ({fV:.0%})"),
      batt(LL,"латынь, как есть"), batt(rewrite(LL,rootL),f"латынь в ядрах ({fL:.0%})")]
show(rows,"БАТАРЕЯ ПРИ ВЫРОВНЕННОЙ ДОЛЕ ВЫВОДА (33 % типов у обоих)")
print("\n  СДВИГИ при равной доле вывода:")
print(f"  {'корпус':>10s} {'TTR':>8s} {'хапакс':>8s} {'длина':>8s} {'h2':>7s} {'слотов':>8s} {'стык1':>8s} {'стык3/1':>9s} {'одинак':>8s} {'похожие':>8s}")
for i in (0,2):
    a,b=rows[i],rows[i+1]; nm="Войнич" if i==0 else "латынь"
    print(f"  {nm:>10s} {b['ttr']-a['ttr']:+8.3f} {b['hx']-a['hx']:+8.3f} {b['ml']-a['ml']:+8.2f} {b['h2']-a['h2']:+7.2f} "
          f"{b['mi']-a['mi']:+8.3f} {b['j1']-a['j1']:+8.3f} {b['jr']-a['jr']:+8.2f}× {b['same']-a['same']:+7.2f}× {b['nearr']-a['nearr']:+7.2f}×")
print("\n"+"="*120); print("ЧТО ОСТАЛОСЬ АНОМАЛЬНЫМ ПОСЛЕ СНЯТИЯ ОБВЕСА (полное снятие, 57 % против латыни 33 %)"); print("="*120)
rf,ff=build_map(S,15); CV=rewrite(VL,rf)
rl,fl2=build_map(SL,400); CL=rewrite(LL,rl)
a,b=batt(CV,"я"),batt(CL,"л")
print(f"  {'мера':>34s} {'ядра Войнича':>14s} {'ядра латыни':>13s} {'разрыв':>9s}")
for key,nm,fmt in [("mi","слотовость (MI знак–позиция)","%.3f"),("h2","условная энтропия h2","%.2f"),
                   ("j1","стык по 1 знаку","%.3f"),("j3","стык по 3 знакам","%.3f"),("jr","стык 3/1","%.2f"),
                   ("same","соседство одинаковых","%.2f"),("nearr","соседство похожих","%.2f"),("ttr","TTR","%.3f")]:
    x,y=a[key],b[key]
    print(f"  {nm:>34s} {fmt%x:>14s} {fmt%y:>13s} {(x/y if y else float('nan')):8.2f}×")
