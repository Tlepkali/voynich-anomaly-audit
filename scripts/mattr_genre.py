# -*- coding: utf-8 -*-
"""Линдеманн 2022 («Crux of the MATTR», CEUR Vol-3313 paper9) помещает
войничский в средний диапазон морфологической сложности, ближе всего к
СРЕДНЕВЕКОВЫМ ГЕРМАНСКИМ, и исключает тюркские и уральские. Меры: MATTR
(скользящий TTR) и MCW (доля десяти самых частых слов). Набор сравнения —
160 языков ИЗ ВИКИПЕДИИ плюс несколько исторических рукописей.

Моя запись E1c показала, что для энтропии жанровый сдвиг вики-против-книги
составляет половину аномалии. Проверяю то же для MATTR и MCW."""
import sys, collections, statistics as st
sys.path.insert(0,"scripts")
import measures as M

def mattr(words, w=2000):
    if len(words)<w: return float("nan")
    vals=[]
    for i in range(0, len(words)-w, max(1,(len(words)-w)//50)):
        seg=words[i:i+w]; vals.append(len(set(seg))/w)
    return st.mean(vals)*100
def mcw(words, k=10):
    c=collections.Counter(words)
    return sum(v for _,v in c.most_common(k))/len(words)*100
VL=M.load(); tv=M.tokens(VL)
N=10000
print("="*92); print("MATTR (окно 2000) И MCW (топ-10), выборки по 10 000 слов"); print("="*92)
print(f"  {'корпус':>16s} {'MATTR':>8s} {'MCW %':>7s}")
print(f"  {'ВОЙНИЧ':>16s} {mattr(tv[:N]):8.1f} {mcw(tv[:N]):7.1f}")
PAIRS=[("английский","bk_en1.clean","wiki_en.clean"),("испанский","bk_es.clean","wiki_es.clean"),
       ("французский","bk_fr1.clean","wiki_fr.clean"),("итальянский","bk_it.clean","wiki_it.clean"),
       ("иврит","scr_tanakh.clean","wiki_he.clean")]
dm=[]; dc=[]
for lab,bk,wk in PAIRS:
    a=M.ref(bk,N); b=M.ref(wk,N)
    if len(a)<N or len(b)<N: continue
    ma,mb=mattr(a),mattr(b); ca,cb=mcw(a),mcw(b)
    dm.append(mb-ma); dc.append(cb-ca)
    print(f"  {lab+', книга':>16s} {ma:8.1f} {ca:7.1f}")
    print(f"  {lab+', вики':>16s} {mb:8.1f} {cb:7.1f}   сдвиг {mb-ma:+.1f} / {cb-ca:+.1f}")
print(f"\n  ЖАНРОВЫЙ СДВИГ: MATTR {st.mean(dm):+.1f} [{min(dm):+.1f}; {max(dm):+.1f}], "
      f"MCW {st.mean(dc):+.1f} [{min(dc):+.1f}; {max(dc):+.1f}]")
v_m, v_c = mattr(tv[:N]), mcw(tv[:N])
books=[(mattr(M.ref(bk,N)), mcw(M.ref(bk,N))) for _,bk,_ in PAIRS if len(M.ref(bk,N))>=N]
print(f"\n  рукопись MATTR {v_m:.1f}, книги {min(x for x,_ in books):.1f}…{max(x for x,_ in books):.1f}")
print(f"  рукопись MCW   {v_c:.1f}, книги {min(y for _,y in books):.1f}…{max(y for _,y in books):.1f}")
print(f"\n  сдвиг MATTR составляет {abs(st.mean(dm)):.1f} пункта; разброс книг "
      f"{max(x for x,_ in books)-min(x for x,_ in books):.1f} пункта")
print("  → " + ("жанр СОПОСТАВИМ с межъязыковым разбросом, для выводов о семье это важно"
      if abs(st.mean(dm))>0.4*(max(x for x,_ in books)-min(x for x,_ in books))
      else "жанр мал против межъязыкового разброса"))
