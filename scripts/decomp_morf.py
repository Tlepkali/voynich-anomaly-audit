# -*- coding: utf-8 -*-
"""Третье разложение — Morfessor Baseline (MDL, установленный инструмент).
Сегментации берутся из самой модели (get_segmentations), а не через viterbi_segment:
последний на обученном словаре возвращает слово целиком."""
import sys, os
sys.path=[p for p in sys.path if os.path.basename(p or ".")!="scripts"]   # scripts/struct.py перекрывает stdlib
import json, collections, random, statistics as st, math
import morfessor
sys.path.insert(0,"scripts")
exec(open("scripts/decomp2.py").read().split('print("="*106)')[0])
def morf_seg(types, counts, cw=1.0, seed=0):
    """ЗЕРНО ОБЯЗАТЕЛЬНО: train_batch перемешивает через глобальный random,
    своего зерна у Morfessor нет. Без него жёсткость ПОСЛЕ снятия гуляет
    9,6-10,7 у рукописи и 7,8-10,2 у латыни, а сдвиг латыни меняет ЗНАК
    между запусками (замерено scripts/morf_spread.py, 03.09.2026)."""
    random.seed(seed)
    m=morfessor.BaselineModel(corpusweight=cw)
    m.load_data([(counts.get(w,1), tuple(w)) for w in types])
    m.train_batch()
    seg={}
    for cnt, compound, parts in m.get_segmentations():
        w="".join(compound) if not isinstance(compound,str) else compound
        seg[w]=["".join(p) if not isinstance(p,str) else p for p in parts]
    return seg
def analyse(lines, lab, cw=1.0, seed=0):
    T=sorted({w for l in lines for w in l})
    cnt=collections.Counter(w for l in lines for w in l)
    seg=morf_seg(T, cnt, cw, seed)
    for w in T: seg.setdefault(w,[w])
    der=sum(1 for w in T if len(seg[w])>1)/len(T)
    root={w:(max(seg[w],key=len) if len(seg[w])>1 else w) for w in T}
    C=[[root.get(w,w) for w in l] for l in lines]
    CT=sorted({w for l in C for w in l})
    return dict(lab=lab, der=der, nm=st.mean(len(seg[w]) for w in T), seg=seg, T=T,
                s1=shape(T), s2=shape(CT), j1=junc1(lines), j2=junc1(C),
                r1=slot_exc(T), r2=slot_exc(CT))
print("="*112); print("MORFESSOR BASELINE (MDL) как третий алгоритм"); print("="*112)
res={}
for lab,L in [("Войнич",VL),("латынь",LL)]:
    r=analyse(L,lab); res[lab]=r
    print(f"  {lab}: выведено {r['der']:.1%}, морфов на слово {r['nm']:.2f}")
    print(f"     плотность {r['s1']:.2f} → {r['s2']:.2f}  сдвиг {r['s2']-r['s1']:+.2f}")
    print(f"     стык 1 знак {r['j1']:.3f} → {r['j2']:.3f}  сдвиг {r['j2']-r['j1']:+.3f}")
    print(f"     слотовость {r['r1']:.2f} → {r['r2']:.2f}  сдвиг {r['r2']-r['r1']:+.2f}")
for lab in ("Войнич","латынь"):
    sg=res[lab]["seg"]; T=res[lab]["T"]
    ex=[w for w in T if len(sg[w])>1][:6]
    sf=collections.Counter(sg[w][-1] for w in T if len(sg[w])>1)
    print(f"\n  {lab}: "+" | ".join("+".join(sg[w]) for w in ex))
    print(f"     частые конечные морфы: "+", ".join(f"{a}·{n}" for a,n in sf.most_common(10)))
print("\n"+"="*112); print("ТРИ АЛГОРИТМА РЯДОМ (Morfessor — среднее 5 засеянных обучений)"); print("="*112)
R5={lab:[analyse(L,lab,seed=sd) for sd in range(5)] for lab,L in [("Войнич",VL),("латынь",LL)]}
def avg(lab,k): return st.mean(r[k] for r in R5[lab])
def rng(lab,k): return (min(r[k] for r in R5[lab]), max(r[k] for r in R5[lab]))
print(f"  {'алгоритм':>32s} {'выв. В.':>9s} {'выв. лат.':>10s} {'В./лат.':>9s} {'плотн.':>8s} {'стык':>8s} {'слотов.':>9s}")
print(f"  {'1: аффикс + слово словаря':>32s} {'57,2 %':>9s} {'15,7 %':>10s} {'3,6×':>9s} {'−0,33':>8s} {'−0,156':>8s} {'−15,8':>9s}")
print(f"  {'2: сигнатуры Голдсмита':>32s} {'24,9 %':>9s} {'28,7 %':>10s} {'0,87×':>9s} {'−0,05':>8s} {'−0,014':>8s} {'−1,02':>9s}")
dv,dl=avg("Войнич","der"),avg("латынь","der")
print(f"  {'3: Morfessor Baseline':>32s} {dv:8.1%} {dl:9.1%} {dv/max(dl,1e-9):8.2f}× "
      f"{avg('Войнич','s2')-avg('Войнич','s1'):+8.2f} {avg('Войнич','j2')-avg('Войнич','j1'):+8.3f} "
      f"{avg('Войнич','r2')-avg('Войнич','r1'):+9.2f}")
print("\n  строки 1 и 2 посчитаны scripts/one_instrument.py тем же измерителем;")
print("  у Morfessor своего зерна нет, поэтому строка 3 — среднее пяти обучений. Разброс:")
for lab in ("Войнич","латынь"):
    a,b=rng(lab,"r2"); c,d=rng(lab,"der")
    print(f"    {lab:>8s}: жёсткость ПОСЛЕ {a:.2f}–{b:.2f}, выведено {c:.1%}–{d:.1%}")
a,b=rng("латынь","r2")
print(f"  сдвиг жёсткости ЛАТЫНИ при этом меняет знак: от {a-avg('латынь','r1'):+.2f} до {b-avg('латынь','r1'):+.2f}")
