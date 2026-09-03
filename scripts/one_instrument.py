# -*- coding: utf-8 -*-
"""Три разложения ОДНИМ прибором.
Повод: §3.1 статьи приводит базовую жёсткость 21,11× (Войнич) и 9,27× (латынь),
§3.2 и §4 — 20,86× и 8,59×. Это одна и та же величина, посчитанная разными
скриптами: старый не задавал зерна перемешивания, новый усредняет 10 засеянных.
Здесь все три алгоритма меряются функциями decomp2 (shape / junc1 / slot_exc)."""
import sys, os
sys.path=[p for p in sys.path if os.path.basename(p or ".")!="scripts"]
import json, collections, random, statistics as st, math
import morfessor
sys.path.insert(0,"scripts")
exec(open("scripts/decomp2.py").read().split('print("="*106)')[0])   # shape, junc1, slot_exc, VL, LL, decompose(Голдсмит)
GOLD=decompose                                                       # чтобы имя не затёрлось

# --- алгоритм 1: аффикс + слово словаря ---
N_TYPES=5000; K_AFF=15
def topN(words,n=N_TYPES):
    c=collections.Counter(words); return [w for w,_ in c.most_common(n)]
def affixes(types,k=K_AFF):
    pre=collections.Counter(); suf=collections.Counter()
    for w in types:
        for L in (1,2,3):
            if len(w)>L: pre[w[:L]]+=1; suf[w[-L:]]+=1
    return [a for a,_ in pre.most_common(k)], [a for a,_ in suf.most_common(k)]
def alg1_cores(lines):
    words=[w for l in lines for w in l]; types=topN(words); S=set(types)
    P,U=affixes(types); derived={}
    for w in sorted(S,key=len):
        for a in P:
            if w.startswith(a) and w[len(a):] in S and len(w[len(a):])>=2: derived[w]=w[len(a):]; break
        if w in derived: continue
        for a in U:
            if w.endswith(a) and w[:-len(a)] in S and len(w[:-len(a)])>=2: derived[w]=w[:-len(a)]; break
    def core(w):
        seen=set()
        while w in derived and w not in seen: seen.add(w); w=derived[w]
        return w
    root={w:core(w) for w in S}
    return [[root.get(w,w) for w in l] for l in lines], len(derived)/len(S)

# --- алгоритм 2: сигнатуры Голдсмита ---
def alg2_cores(lines):
    T=sorted({w for l in lines for w in l}); root,der=GOLD(T)
    return [[root.get(w,w) for w in l] for l in lines], der

# --- алгоритм 3: Morfessor ---
def alg3_cores(lines, seed):
    random.seed(seed)
    T=sorted({w for l in lines for w in l}); cnt=collections.Counter(w for l in lines for w in l)
    m=morfessor.BaselineModel(corpusweight=1.0)
    m.load_data([(cnt.get(w,1), tuple(w)) for w in T]); m.train_batch()
    seg={}
    for c,comp,parts in m.get_segmentations():
        w="".join(comp) if not isinstance(comp,str) else comp
        seg[w]=["".join(p) if not isinstance(p,str) else p for p in parts]
    root={w:(max(seg[w],key=len) if len(seg.get(w,[w]))>1 else w) for w in T}
    der=sum(1 for w in T if len(seg.get(w,[w]))>1)/len(T)
    return [[root.get(w,w) for w in l] for l in lines], der

def measure(L,C):
    T=sorted({w for l in L for w in l}); CT=sorted({w for l in C for w in l})
    return shape(T),shape(CT),junc1(L),junc1(C),slot_exc(T),slot_exc(CT)

print("="*118); print("БАЗОВЫЕ ЗНАЧЕНИЯ (до всякого разложения), измеритель decomp2, 10 засеянных перемешиваний"); print("="*118)
for lab,L in [("Войнич",VL),("латынь",LL)]:
    T=sorted({w for l in L for w in l})
    print(f"  {lab:>8s}: профиль плотности {shape(T):.2f}   стык 1 знак {junc1(L):.3f}   жёсткость типов {slot_exc(T):.2f}×")
print("\n"+"="*118); print("ТРИ АЛГОРИТМА, ОДИН ПРИБОР"); print("="*118)
print(f"  {'алгоритм':>28s} {'корпус':>8s} {'выведено':>9s} | {'плотн. до→после':>18s} {'сдвиг':>7s} | {'стык до→после':>16s} {'сдвиг':>7s} | {'жёстк. до→после':>18s} {'сдвиг':>7s}")
rows={}
for anm,fn in [("1: аффикс + слово словаря",alg1_cores),("2: сигнатуры Голдсмита",alg2_cores),("3: Morfessor Baseline",None)]:
    for lab,L in [("Войнич",VL),("латынь",LL)]:
        if fn is None:
            R=[]
            for s in range(5):
                C,der=alg3_cores(L,s); R.append(measure(L,C)+(der,))
            s1=R[0][0]; s2=st.mean(r[1] for r in R); j1=R[0][2]; j2=st.mean(r[3] for r in R)
            m1=R[0][4]; m2=st.mean(r[5] for r in R); der=st.mean(r[6] for r in R)
            sp=f"  [разброс жёсткости после: {min(r[5] for r in R):.2f}–{max(r[5] for r in R):.2f}]"
        else:
            C,der=fn(L); s1,s2,j1,j2,m1,m2=measure(L,C); sp=""
        rows[(anm,lab)]=(der,s1,s2,j1,j2,m1,m2)
        print(f"  {anm:>28s} {lab:>8s} {der:8.1%} | {s1:8.2f} →{s2:7.2f} {s2-s1:+7.2f} | {j1:7.3f} →{j2:6.3f} {j2-j1:+7.3f} | {m1:8.2f} →{m2:7.2f} {m2-m1:+7.2f}{sp}")
print("\n  Morfessor: среднее по 5 засеянным обучениям (у алгоритма нет зерна по умолчанию)")
print("\n"+"="*118); print("СВОДКА ДЛЯ §3.2 СТАТЬИ"); print("="*118)
print(f"  {'алгоритм':>28s} {'выв. В.':>9s} {'выв. лат.':>10s} {'В./лат.':>9s} {'плотн.':>8s} {'стык':>8s} {'жёстк.':>8s}")
for anm in ("1: аффикс + слово словаря","2: сигнатуры Голдсмита","3: Morfessor Baseline"):
    v=rows[(anm,"Войнич")]; l=rows[(anm,"латынь")]
    print(f"  {anm:>28s} {v[0]:8.1%} {l[0]:9.1%} {v[0]/l[0]:8.2f}× {v[2]-v[1]:+8.2f} {v[4]-v[3]:+8.3f} {v[6]-v[5]:+8.2f}")
print("\n  жёсткость ПОСЛЕ, по корпусам:")
for anm in ("1: аффикс + слово словаря","2: сигнатуры Голдсмита","3: Morfessor Baseline"):
    v=rows[(anm,"Войнич")]; l=rows[(anm,"латынь")]
    print(f"    {anm:>28s}: Войнич {v[6]:.2f}× латынь {l[6]:.2f}× разрыв {v[6]/l[6]:.2f}×")
