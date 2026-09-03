# -*- coding: utf-8 -*-
"""Остаток СТРОК-ПРОДОЛЖЕНИЙ: приписывание объясняет только треть.
Что за слова стоят в начале, если не приписанные.
Плюс контроль на слитных алфавитах: не артефакт ли это EVA-диграфов (c = ch/cth)."""
import json, collections, statistics as st, sys

def rows_of(code):
    D=json.load(open(f"data/parsed_{code}.json"))
    R=[r for r in D["rows"] if r["locus"]=="P"]
    for r in R: r["w"]=[w for w in r["words"] if "?" not in w]
    return [r for r in R if len(r["w"])>=3]

def report(code, lab):
    R=rows_of(code); C=[r for r in R if r["pos"]=="+"]
    if len(C)<200: print(f"  {lab}: строк-продолжений мало ({len(C)})"); return
    VT={w for r in R for w in r["w"]}
    MID=[w for r in R for w in r["w"][1:]]
    mid=collections.Counter(w[0] for w in MID); b=sum(mid.values())
    FI=[r["w"][0] for r in C]
    dec=[w for w in FI if len(w)>2 and w[1:] in VT]      # раскладывается как знак+слово
    ind=[w for w in FI if not (len(w)>2 and w[1:] in VT)] # не раскладывается
    print(f"\n  {lab}: строк-продолжений {len(C)}, раскладывается {len(dec)/len(FI):.1%}, "
          f"длина нач./сер. {st.mean(len(w) for w in FI):.2f}/{st.mean(len(w) for w in MID):.2f}")
    print(f"    {'группа':>26s} {'n':>5s} " + " ".join(f"{c:>6s}" for c,_ in mid.most_common(8)))
    print(f"    {'СЕРЕДИНА строки':>26s} {len(MID):5d} " + " ".join(f"{mid[c]/b:5.1%}" for c,_ in mid.most_common(8)))
    for nm,W in [("начальные, разложимые",dec),("начальные, НЕразложимые",ind)]:
        f=collections.Counter(w[0] for w in W); a=sum(f.values())
        print(f"    {nm:>26s} {len(W):5d} " + " ".join(f"{f[c]/a:5.1%}" for c,_ in mid.most_common(8)))
    # остаток У НЕРАЗЛОЖИМЫХ: они по определению НЕ приписаны, значит это ВЫБОР СЛОВА
    f=collections.Counter(w[0] for w in ind); a=sum(f.values())
    tv=sum(abs(f[c]/a-mid[c]/b) for c in set(f)|set(mid))/2
    print(f"    расхождение НЕразложимых с серединой: {tv:.3f}   ← приписывание тут ни при чём")
    # и у разложимых, после снятия приписанного знака
    st_=collections.Counter(w[1:][0] for w in dec); a2=sum(st_.values())
    tv2=sum(abs(st_[c]/a2-mid[c]/b) for c in set(st_)|set(mid))/2
    print(f"    расхождение ОСТАТКОВ (знак снят)     : {tv2:.3f}   ← если 0, приписывание объясняет всё")

print("="*104); print("СТРОКИ-ПРОДОЛЖЕНИЯ: две группы начальных слов"); print("="*104)
for code,lab in [("ZL3b-n","EVA, Зандберген–Ландини"),("IT2a-n","EVA, Такахаси"),
                 ("GC2a-n","v101, Класton (ch — ОДИН знак)"),("FG2a-n","FSG")]:
    try: report(code,lab)
    except Exception as e: print(f"  {lab}: {e}")
