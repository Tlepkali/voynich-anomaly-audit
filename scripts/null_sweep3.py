# -*- coding: utf-8 -*-
"""A12 — единственная положительная находка работы: цепь по знакам заново
порождает 28,8 % словаря против 1,7–6,6 % у языков, ВЫРОВНЕННЫХ по числу типов
и длине слова. Третьей оси выравнивания нет: ЭФФЕКТИВНЫЙ РАЗМЕР АЛФАВИТА.
Меньше алфавит — меньше пространство слов — легче попасть.

Контроль в той же форме, что применён к ранг-корреляции (§6 аудита):
регрессия доли порождения на эффективный алфавит по всем корпусам,
и остаток рукописи в единицах стандартного отклонения.
"""
import sys, math, collections, statistics as st
sys.path.insert(0,"scripts")
import measures as M

def eff_alpha(types):
    """перплексия распределения знаков: 2^h1, «сколько знаков на деле»"""
    c=collections.Counter(ch for w in types for ch in w); n=sum(c.values())
    h=-sum(v/n*math.log2(v/n) for v in c.values())
    return 2**h, len(c)
VL=M.load(); TV=M.types(VL); mV=st.mean(len(w) for w in TV)
REFS=[("латынь","latin.clean"),("англ. книга 1","bk_en1.clean"),("англ. книга 2","bk_en2.clean"),
      ("англ. корпус","english.clean"),("исп. книга","bk_es.clean"),("итал. книга","bk_it.clean"),
      ("франц. книга 1","bk_fr1.clean"),("травник","g_herbal.clean"),("Вульгата","scr_vulgata.clean"),
      ("Коран","scr_quran.clean"),("Танах","scr_tanakh.clean"),("вики монг.","wiki_mn.clean"),
      ("вики иврит","wiki_he.clean"),("вики англ.","wiki_en.clean"),("вики исп.","wiki_es.clean")]
rows=[]
ea,na=eff_alpha(TV)
rg=st.mean(M.regeneration(TV,2,s) for s in range(3))
rows.append(("ВОЙНИЧ",ea,na,mV,rg,len(TV)))
print("="*104); print("ЭФФЕКТИВНЫЙ АЛФАВИТ И ПОРОЖДЕНИЕ (словари выровнены: 7205 типов, длина как у рукописи)"); print("="*104)
print(f"  {'корпус':>15s} {'знаков':>7s} {'эфф. алфавит':>13s} {'ср.длина':>9s} {'порождение':>11s}")
print(f"  {'ВОЙНИЧ':>15s} {na:7d} {ea:13.2f} {mV:9.2f} {rg:11.1%}")
for lab,fn in REFS:
    T=sorted(set(M.ref(fn)))
    if len(T)<len(TV): continue
    Mt=M.match_mean_length(T,len(TV),mV,seed=0)
    if len(Mt)<len(TV)*0.9: continue
    e,n_=eff_alpha(Mt); m_=st.mean(len(w) for w in Mt)
    r=st.mean(M.regeneration(Mt,2,s) for s in range(3))
    rows.append((lab,e,n_,m_,r,len(Mt)))
    print(f"  {lab:>15s} {n_:7d} {e:13.2f} {m_:9.2f} {r:11.1%}")
print("\n"+"="*104); print("РЕГРЕССИЯ ПОРОЖДЕНИЯ НА ЭФФЕКТИВНЫЙ АЛФАВИТ"); print("="*104)
xs=[r[1] for r in rows]; ys=[r[4] for r in rows]
mx,my=st.mean(xs),st.mean(ys)
b=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs); a=my-b*mx
res=[(r[0], r[4]-(a+b*r[1])) for r in rows]
sd=st.pstdev([e for _,e in res])
print(f"  наклон {b:+.4f} на знак эффективного алфавита; sd остатков {sd:.4f}")
print(f"\n  {'корпус':>15s} {'предсказано':>12s} {'наблюдено':>10s} {'остаток, sd':>12s}")
for (lab,e_),(l2,x,n_,m_,y,_) in zip(res,rows):
    print(f"  {lab:>15s} {(a+b*x):12.1%} {y:10.1%} {e_/sd:+12.2f}")
z=[e/sd for l,e in res if l=="ВОЙНИЧ"][0]
print(f"\n  остаток рукописи {z:+.2f} sd при {len(rows)} корпусах; ожидаемый максимум "
      f"{len(rows)} нормальных отклонений ≈ {1.5+0.5*math.log(len(rows)):.1f}")
print(f"  {'ВЫШЕ ожидаемого максимума — находка держится' if z>1.5+0.5*math.log(len(rows)) else 'НЕ выше — эффективный алфавит объясняет'}")
