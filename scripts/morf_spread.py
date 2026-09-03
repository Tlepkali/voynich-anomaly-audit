# -*- coding: utf-8 -*-
"""Разброс чисел Morfessor от запуска к запуску: ни зерна, ни у обучения, ни у перемешивания."""
import sys, os
sys.path=[p for p in sys.path if os.path.basename(p or ".")!="scripts"]
import json, collections, random, statistics as st, math
import morfessor
sys.path.insert(0,"scripts")
exec(open("scripts/decomp_morf.py").read().split('print("="*112)')[0].split('import morfessor')[1].replace('sys.path.insert(0,"scripts")','',1))
N=5
acc=collections.defaultdict(list)
for i in range(N):
    for lab,L in [("Войнич",VL),("латынь",LL)]:
        r=analyse(L,lab)
        acc[(lab,"выведено, %")].append(r['der']*100)
        acc[(lab,"морфов/слово")].append(r['nm'])
        acc[(lab,"сдвиг плотности")].append(r['s2']-r['s1'])
        acc[(lab,"сдвиг стыка")].append(r['j2']-r['j1'])
        acc[(lab,"жёсткость ДО")].append(r['r1'])
        acc[(lab,"жёсткость ПОСЛЕ")].append(r['r2'])
        acc[(lab,"сдвиг жёсткости")].append(r['r2']-r['r1'])
print("="*100); print(f"РАЗБРОС ПО {N} ЗАПУСКАМ (зерно нигде не задано)"); print("="*100)
print(f"  {'корпус':>8s} {'величина':>18s} {'среднее':>10s} {'мин':>9s} {'макс':>9s} {'размах':>9s} {'в статье':>10s}")
PAP={("Войнич","выведено, %"):88.0,("латынь","выведено, %"):62.9,
     ("Войнич","морфов/слово"):2.14,("Войнич","сдвиг плотности"):-0.01,
     ("латынь","сдвиг плотности"):-0.26,("Войнич","сдвиг стыка"):-0.070,
     ("Войнич","жёсткость ДО"):20.86,("Войнич","жёсткость ПОСЛЕ"):10.41,
     ("латынь","жёсткость ДО"):8.59,("латынь","жёсткость ПОСЛЕ"):9.80,
     ("Войнич","сдвиг жёсткости"):-10.44}
for k,v in acc.items():
    p=PAP.get(k); ps=f"{p:10.2f}" if p is not None else " "*10
    print(f"  {k[0]:>8s} {k[1]:>18s} {st.mean(v):10.3f} {min(v):9.3f} {max(v):9.3f} {max(v)-min(v):9.3f} {ps}")
