# -*- coding: utf-8 -*-
"""КОНТРОЛЬ к остатку строки. Утверждение: сняв приписанный знак с начального
слова, получаем остаток, который ВСЁ ЕЩЁ не похож на обычное слово (0,319).
Но отбор «разложимых» сам по себе перекошен. Поэтому та же операция
применяется к словам СЕРЕДИНЫ строки: берём разложимые, снимаем первый знак,
смотрим расхождение остатков с обычными словами середины.
Если у середины выходит столько же — 0,319 говорит о процедуре, а не о строке."""
import json, collections, statistics as st, random

def load(code):
    D=json.load(open(f"data/parsed_{code}.json"))
    R=[r for r in D["rows"] if r["locus"]=="P"]
    for r in R: r["w"]=[w for w in r["words"] if "?" not in w]
    return [r for r in R if len(r["w"])>=3]

def tv(c1,c2):
    a=sum(c1.values()); b=sum(c2.values())
    return sum(abs(c1[c]/a-c2[c]/b) for c in set(c1)|set(c2))/2

print("="*100); print("КОНТРОЛЬ: та же операция снятия знака на середине строки"); print("="*100)
print(f"  {'транскрипция':>26s} {'начало: остатки':>16s} {'СЕРЕДИНА: остатки':>18s} {'разница':>9s}")
for code,lab in [("ZL3b-n","EVA Зандб.–Ландини"),("IT2a-n","EVA Такахаси"),
                 ("GC2a-n","v101 Класton"),("FG2a-n","FSG")]:
    R=load(code); C=[r for r in R if r["pos"]=="+"]
    VT={w for r in R for w in r["w"]}
    MID=[w for r in R for w in r["w"][1:]]
    mid=collections.Counter(w[0] for w in MID)
    FI=[r["w"][0] for r in C]
    # остатки НАЧАЛЬНЫХ слов
    s_fi=collections.Counter(w[1] for w in FI if len(w)>2 and w[1:] in VT)
    # остатки СЕРЕДИННЫХ слов — та же процедура, тот же отбор
    s_mid=collections.Counter(w[1] for w in MID if len(w)>2 and w[1:] in VT)
    a,b=tv(s_fi,mid), tv(s_mid,mid)
    print(f"  {lab:>26s} {a:16.3f} {b:18.3f} {a-b:+9.3f}")
print("\n  если разница около нуля — 0,32 у начала строки есть свойство ПРОЦЕДУРЫ отбора,")
print("  а не свойство начала строки, и утверждение об остатке снимается")

print("\n"+"="*100); print("ТО ЖЕ, НО ПРЯМЫМ СРАВНЕНИЕМ ОСТАТКОВ МЕЖДУ СОБОЙ"); print("="*100)
print(f"  {'транскрипция':>26s} {'остатки нач. против остатков сер.':>34s}")
for code,lab in [("ZL3b-n","EVA Зандб.–Ландини"),("IT2a-n","EVA Такахаси"),
                 ("GC2a-n","v101 Класton"),("FG2a-n","FSG")]:
    R=load(code); C=[r for r in R if r["pos"]=="+"]
    VT={w for r in R for w in r["w"]}
    MID=[w for r in R for w in r["w"][1:]]
    FI=[r["w"][0] for r in C]
    s_fi=collections.Counter(w[1] for w in FI if len(w)>2 and w[1:] in VT)
    s_mid=collections.Counter(w[1] for w in MID if len(w)>2 and w[1:] in VT)
    print(f"  {lab:>26s} {tv(s_fi,s_mid):34.3f}")
print("\n  это и есть чистая величина: насколько остаток начального слова отличается")
print("  от остатка серединного, когда с обоих снят первый знак одинаковой процедурой")
