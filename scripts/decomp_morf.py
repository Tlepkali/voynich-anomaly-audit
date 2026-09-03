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
def morf_seg(types, counts, cw=1.0):
    m=morfessor.BaselineModel(corpusweight=cw)
    m.load_data([(counts.get(w,1), tuple(w)) for w in types])
    m.train_batch()
    seg={}
    for cnt, compound, parts in m.get_segmentations():
        w="".join(compound) if not isinstance(compound,str) else compound
        seg[w]=["".join(p) if not isinstance(p,str) else p for p in parts]
    return seg
def analyse(lines, lab, cw=1.0):
    T=sorted({w for l in lines for w in l})
    cnt=collections.Counter(w for l in lines for w in l)
    seg=morf_seg(T, cnt, cw)
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
print("\n"+"="*112); print("ТРИ АЛГОРИТМА РЯДОМ"); print("="*112)
print(f"  {'алгоритм':>32s} {'выв. В.':>9s} {'выв. лат.':>10s} {'В./лат.':>9s} {'плотн.':>8s} {'стык':>8s} {'слотов.':>9s}")
print(f"  {'1: аффикс + слово словаря':>32s} {'57,2 %':>9s} {'15,7 %':>10s} {'3,6×':>9s} {'−0,33':>8s} {'−0,157':>8s} {'−16,3':>9s}")
print(f"  {'2: сигнатуры Голдсмита':>32s} {'24,9 %':>9s} {'28,7 %':>10s} {'0,87×':>9s} {'−0,05':>8s} {'−0,014':>8s} {'−1,02':>9s}")
V,Lr=res["Войнич"],res["латынь"]
print(f"  {'3: Morfessor Baseline':>32s} {V['der']:8.1%} {Lr['der']:9.1%} {V['der']/max(Lr['der'],1e-9):8.2f}× "
      f"{V['s2']-V['s1']:+8.2f} {V['j2']-V['j1']:+8.3f} {V['r2']-V['r1']:+9.2f}")
