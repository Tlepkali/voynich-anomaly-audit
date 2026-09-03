# -*- coding: utf-8 -*-
"""Алгоритм 1 на корпусах, ВЫРАВНЕННЫХ по объёму рукописи (34 024 токена).
В §3.1 статьи стояли 30,1 / 18,9 / 17,0 / 9,9 % — они считались на файлах целиком
и на наборе, куда входил немецкий, которого в ref/ нет."""
import sys, os
sys.path=[p for p in sys.path if os.path.basename(p or ".")!="scripts"]
import json, collections, random, statistics as st, math
sys.path.insert(0,"scripts")
exec(open("scripts/decomp2.py").read().split('print("="*106)')[0])
def affixes(types,k=15):
    pre=collections.Counter(); suf=collections.Counter()
    for w in types:
        for L in (1,2,3):
            if len(w)>L: pre[w[:L]]+=1; suf[w[-L:]]+=1
    return [a for a,_ in pre.most_common(k)],[a for a,_ in suf.most_common(k)]
def alg1(words, ntypes=None, minrem=2):
    types=[w for w,_ in collections.Counter(words).most_common(ntypes)] if ntypes else sorted(set(words))
    S=set(types); P,U=affixes(types); derived={}; twice=0
    for w in sorted(S,key=len):
        for a in P:
            if w.startswith(a) and w[len(a):] in S and len(w[len(a):])>=minrem: derived[w]=w[len(a):]; break
        if w in derived: continue
        for a in U:
            if w.endswith(a) and w[:-len(a)] in S and len(w[:-len(a)])>=minrem: derived[w]=w[:-len(a)]; break
    for w in S:
        x=w; d=0; seen=set()
        while x in derived and x not in seen: seen.add(x); x=derived[x]; d+=1
        if d>=2: twice+=1
    return len(derived)/len(S), twice/len(S), len(S)
V=[w for l in VL for w in l]
print("="*100); print("АЛГОРИТМ 1, ВСЕ ТИПЫ (настройка таблицы §3.2), корпуса по 34 024 токена"); print("="*100)
print(f"  {'корпус':>16s} {'токенов':>8s} {'типов':>7s} {'выведено':>9s} {'сводится ≥2 раз':>16s}")
r=alg1(V); print(f"  {'ВОЙНИЧ':>16s} {len(V):8d} {r[2]:7d} {r[0]:8.1%} {r[1]:15.1%}")
rnd=random.Random(7)
# контроль должен перемешивать ТИПЫ (иначе число типов утраивается и сравнение теряет смысл)
TV=sorted(set(V)); mp={w:"".join(rnd.sample(w,len(w))) for w in TV}
sh=[mp[w] for w in V]
r=alg1(sh); print(f"  {'перемешка типов':>16s} {len(sh):8d} {r[2]:7d} {r[0]:8.1%} {r[1]:15.1%}")
sh2=["".join(rnd.sample(w,len(w))) for w in V]
r=alg1(sh2); print(f"  {'перемешка токенов':>16s} {len(sh2):8d} {r[2]:7d} {r[0]:8.1%} {r[1]:15.1%}   ← не тот контроль: типов втрое больше")
for fn,lab in [("latin.clean","латынь"),("english.clean","английский"),("bk_it.clean","итальянский"),
               ("bk_es.clean","испанский"),("bk_fr1.clean","французский"),("scr_vulgata.clean","Вульгата")]:
    w=open("ref/"+fn,encoding="utf-8",errors="ignore").read().split()[:len(V)]
    r=alg1(w); print(f"  {lab:>16s} {len(w):8d} {r[2]:7d} {r[0]:8.1%} {r[1]:15.1%}")
print("\n  для сверки — как было в §3.1 (файлы целиком, не выравнены):")
for fn,lab in [("latin.clean","латынь"),("english.clean","английский"),("bk_it.clean","итальянский")]:
    w=open("ref/"+fn,encoding="utf-8",errors="ignore").read().split()
    r=alg1(w); print(f"  {lab:>16s} {len(w):8d} {r[2]:7d} {r[0]:8.1%} {r[1]:15.1%}")
