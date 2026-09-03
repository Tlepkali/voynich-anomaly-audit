# -*- coding: utf-8 -*-
"""Записи инвентаря с ПУСТЫМ контролем: B9, E2, E3.

B9 «автокорреляция длины слова положительна, у языков отрицательна» — CONFIRM
при контроле «—», и это ОДНА ИЗ ЧЕТЫРЁХ ПОДПИСЕЙ генеративной статьи.
E2 «текст следует закону Ципфа» — CONFIRM при контроле «—».
E3 «доля одноразовых слов языковая» — CONFIRM при сравнении с ОДНОЙ латынью,
что прямо нарушает собственное правило статьи (набор сравнения по двум осям).

Здесь всем троим даётся то, чего не было: 18 корпусов по 34 024 токена,
нулевая модель, интервалы.
"""
import sys, math, random, collections, statistics as st
sys.path.insert(0,"scripts")
import measures as M

VL=M.load(); LENS=[len(l) for l in VL]; NTOK=sum(LENS)
REFS=[("латынь","latin.clean"),("англ. книга 1","bk_en1.clean"),("англ. книга 2","bk_en2.clean"),
      ("англ. корпус","english.clean"),("исп. книга","bk_es.clean"),("итал. книга","bk_it.clean"),
      ("франц. книга 1","bk_fr1.clean"),("франц. книга 2","bk_fr2.clean"),("травник","g_herbal.clean"),
      ("Вульгата","scr_vulgata.clean"),("Коран","scr_quran.clean"),("Танах","scr_tanakh.clean"),
      ("вики монг.","wiki_mn.clean"),("вики иврит","wiki_he.clean"),("вики англ.","wiki_en.clean"),
      ("вики исп.","wiki_es.clean"),("вики франц.","wiki_fr.clean"),("вики итал.","wiki_it.clean")]

def hapax(L):
    c=collections.Counter(M.tokens(L)); return sum(1 for v in c.values() if v==1)/len(c)
def zipf(L):
    c=collections.Counter(M.tokens(L)); f=sorted(c.values(),reverse=True)
    n=min(len(f),3000); xs=[math.log(i+1) for i in range(n)]; ys=[math.log(v) for v in f[:n]]
    mx,my=st.mean(xs),st.mean(ys)
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)
def shuffle_in_line(L, seed):
    rnd=random.Random(seed); out=[]
    for l in L:
        c=l[:]; rnd.shuffle(c); out.append(c)
    return out

print("="*104); print("B9: АВТОКОРРЕЛЯЦИЯ ДЛИНЫ СЛОВА, лаг 1 — 18 корпусов по 34 024 токена"); print("="*104)
obs=M.len_autocorr(VL)
nl=[M.len_autocorr(shuffle_in_line(VL,s)) for s in range(200)]
ge=sum(1 for x in nl if x>=obs)
print(f"  РУКОПИСЬ {obs:+.4f}   нуль (перемешивание ВНУТРИ СТРОКИ, 200): {st.mean(nl):+.4f} "
      f"[{min(nl):+.4f}; {max(nl):+.4f}]  p = {(ge+1)/201:.4f}")
print(f"\n  {'корпус':>16s} {'r(1)':>9s} {'нуль внутри строк':>19s} {'знак':>6s}")
vals=[]
for lab,fn in REFS:
    L=M.ref_lines(fn,LENS)
    if len(L)<len(LENS)*0.9: continue
    r=M.len_autocorr(L)
    n2=[M.len_autocorr(shuffle_in_line(L,s)) for s in range(20)]
    vals.append((lab,r))
    print(f"  {lab:>16s} {r:+9.4f} {st.mean(n2):+13.4f} {'плюс' if r>0 else 'минус':>10s}")
pos=[v for _,v in vals if v>0]
print(f"\n  положительных среди 18: {len(pos)}   диапазон языков: {min(v for _,v in vals):+.4f}…{max(v for _,v in vals):+.4f}")
print(f"  рукопись {obs:+.4f} — {'ВЫШЕ ВСЕХ' if obs>max(v for _,v in vals) else 'НЕ выше всех'}")

print("\n"+"="*104); print("E3: ДОЛЯ ОДНОРАЗОВЫХ СЛОВ (в записи стояло сравнение с ОДНОЙ латынью)"); print("="*104)
h=hapax(VL); hs=[(lab,hapax(M.ref_lines(fn,LENS))) for lab,fn in REFS]
lo,hi=min(v for _,v in hs),max(v for _,v in hs)
print(f"  РУКОПИСЬ {h:.3f}   18 корпусов: {lo:.3f}…{hi:.3f}   "
      f"{'ВНУТРИ' if lo<=h<=hi else 'ВНЕ'} языкового диапазона")
in_r=sorted(hs,key=lambda x:x[1])
print("  крайние: " + ", ".join(f"{l} {v:.3f}" for l,v in in_r[:3]) + " … " + ", ".join(f"{l} {v:.3f}" for l,v in in_r[-3:]))

print("\n"+"="*104); print("E2: НАКЛОН ЦИПФА (в записи контроля не было вовсе)"); print("="*104)
z=zipf(VL); zs=[(lab,zipf(M.ref_lines(fn,LENS))) for lab,fn in REFS]
lo,hi=min(v for _,v in zs),max(v for _,v in zs)
print(f"  РУКОПИСЬ {z:.3f}   18 корпусов: {lo:.3f}…{hi:.3f}   "
      f"{'ВНУТРИ' if lo<=z<=hi else 'ВНЕ'} языкового диапазона")
print("  крайние: " + ", ".join(f"{l} {v:.2f}" for l,v in sorted(zs,key=lambda x:x[1])[:3]) +
      " … " + ", ".join(f"{l} {v:.2f}" for l,v in sorted(zs,key=lambda x:x[1])[-3:]))
