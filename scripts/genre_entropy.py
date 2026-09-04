# -*- coding: utf-8 -*-
"""Линдеманн и Боуэрн 2020: условная энтропия рукописи «отлична от КАЖДОГО
сравнительного текста». Их набор — 294 образца ВИКИПЕДИИ плюс 18 исторических.
Мой §6 установил, что жанровый сдвиг вики-против-книги на ранг-корреляции
превышает сам сигнал. Задевает ли жанр их меру?

Считаю h2 знакового потока для пяти языков, где у меня есть И книга, И вики,
на равном объёме, и сравниваю жанровый сдвиг с разрывом рукопись-язык.
"""
import sys, statistics as st
sys.path.insert(0,"scripts")
import measures as M

VL=M.load(); N=len(M.tokens(VL))
def h2_words(words):
    L=[]; row=[]
    for w in words:
        row.append(w)
        if len(row)==8: L.append(row); row=[]
    return M.h2_stream(L)
PAIRS=[("английский","bk_en1.clean","wiki_en.clean"),
       ("испанский","bk_es.clean","wiki_es.clean"),
       ("французский","bk_fr1.clean","wiki_fr.clean"),
       ("итальянский","bk_it.clean","wiki_it.clean"),
       ("иврит","scr_tanakh.clean","wiki_he.clean")]
voy=M.h2_stream(VL)
print("="*96); print(f"h2 ЗНАКОВОГО ПОТОКА: КНИГА ПРОТИВ ВИКИПЕДИИ (рукопись {voy:.3f})"); print("="*96)
print(f"  {'язык':>14s} {'книга':>8s} {'вики':>8s} {'сдвиг':>8s} {'разрыв с рукописью':>20s}")
shifts=[]
for lab,bk,wk in PAIRS:
    a=h2_words(M.ref(bk, N)); b=h2_words(M.ref(wk, N))
    n=min(len(M.ref(bk)),len(M.ref(wk)),N)
    a=h2_words(M.ref(bk,n)); b=h2_words(M.ref(wk,n))
    shifts.append(b-a)
    print(f"  {lab:>14s} {a:8.3f} {b:8.3f} {b-a:+8.3f} {min(a,b)-voy:19.3f}")
print(f"\n  средний жанровый сдвиг {st.mean(shifts):+.3f}, размах {min(shifts):+.3f}…{max(shifts):+.3f}")
gaps=[]
for lab,bk,wk in PAIRS:
    n=min(len(M.ref(bk)),len(M.ref(wk)),N)
    gaps.append(min(h2_words(M.ref(bk,n)), h2_words(M.ref(wk,n)))-voy)
print(f"  минимальный разрыв рукопись-язык {min(gaps):.3f}")
print(f"\n  жанровый сдвиг составляет {abs(st.mean(shifts))/min(gaps):.1%} от разрыва")
print("  ВЫВОД: " + ("жанр их вывода НЕ задевает — сдвиг мал против разрыва"
      if abs(max(shifts, key=abs))<min(gaps)*0.5 else "жанр СОПОСТАВИМ с разрывом, оговорка нужна"))
