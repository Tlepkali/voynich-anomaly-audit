# -*- coding: utf-8 -*-
"""Аманчио и др. 2013 (PLOS ONE): у рукописи среди немногих ОТКЛОНЕНИЙ от
языковой нормы — «необычно высокая дисперсия перемежаемости» (intermittency).
У меня запись B8 «профиль возврата слова языковой» стоит ПОДТВЕРЖДЁННОЙ.
Проверяю стандартным коэффициентом прерывистости Го и Барабаши:
B = (sd - mean) / (sd + mean) по интервалам между вхождениями слова.
B = -1 строго периодично, 0 пуассоновский поток, +1 крайне прерывисто.
"""
import sys, collections, random, statistics as st
sys.path.insert(0,"scripts")
import measures as M

def burst(tokens, minocc=10):
    pos=collections.defaultdict(list)
    for i,w in enumerate(tokens): pos[w].append(i)
    B=[]; W=[]
    for w,ii in pos.items():
        if len(ii)<minocc: continue
        d=[b-a for a,b in zip(ii,ii[1:])]
        m=st.mean(d); s=st.pstdev(d)
        if m+s>0: B.append((s-m)/(s+m)); W.append(len(ii))
    return st.mean(B), st.pstdev(B), len(B)

VL=M.load(); LENS=[len(l) for l in VL]
tv=M.tokens(VL)
print("="*96); print("КОЭФФИЦИЕНТ ПРЕРЫВИСТОСТИ B = (sd-mean)/(sd+mean) по интервалам возврата слова"); print("="*96)
print(f"  {'корпус':>16s} {'слов':>6s} {'среднее B':>10s} {'sd B':>7s}")
rows=[("ВОЙНИЧ", tv)]
for fn,lab in [("latin.clean","латынь"),("english.clean","английский"),("bk_it.clean","итальянский"),
               ("bk_es.clean","испанский"),("g_herbal.clean","травник"),("scr_vulgata.clean","Вульгата"),
               ("bk_fr1.clean","французский")]:
    rows.append((lab, M.ref(fn, len(tv))))
for lab,T in rows:
    m,s,n=burst(T)
    print(f"  {lab:>16s} {n:6d} {m:10.4f} {s:7.4f}")
print("\n  контроли для рукописи:")
rnd=random.Random(9); sh=tv[:]; rnd.shuffle(sh)
m,s,n=burst(sh); print(f"  {'перемешка всего':>16s} {n:6d} {m:10.4f} {s:7.4f}")
SH=[]
for l in VL:
    c=l[:]; rnd.shuffle(c); SH.append(c)
m,s,n=burst(M.tokens(SH)); print(f"  {'внутри строк':>16s} {n:6d} {m:10.4f} {s:7.4f}")
print("\n  и то же для языков после полного перемешивания (для масштаба):")
for lab,T in rows[1:4]:
    t=T[:]; random.Random(3).shuffle(t)
    m,s,n=burst(t); print(f"  {lab+', перемешан':>16s} {n:6d} {m:10.4f} {s:7.4f}")
