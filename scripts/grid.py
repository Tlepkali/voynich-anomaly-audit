# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys, math
exec(open("scripts/coretext.py").read().split("root,frac=build_map")[0])
S=set(VOY)
rV,fV=build_map(S,15); CORES_V=sorted(set(rV.values()))
lw=open("ref/latin.clean").read().split()
LL=[];p=0
for l in VL:
    if p+len(l)>len(lw): break
    LL.append(lw[p:p+len(l)]); p+=len(l)
SL=set(w for l in LL for w in l)
rL,fL=build_map(SL,400); CORES_L=sorted(set(rL.values()))
def shuf_words(ws,seed=0):
    rnd=random.Random(seed); out=set()
    for w in ws:
        c=list(w); rnd.shuffle(c); out.add("".join(c))
    return sorted(out)
CORES_SH=shuf_words(CORES_V)
print(f"ядер: рукопись {len(CORES_V)}, латынь {len(CORES_L)}, контроль-перемешка {len(CORES_SH)}")
print("="*112); print("ЗАПОЛНЕННОСТЬ ПОЗИЦИОННОЙ РЕШЁТКИ: сколько узлов сетки реально занято"); print("="*112)
print(f"  {'набор':>22s} {'длина':>6s} {'слов':>6s} {'алфавиты по позициям':>24s} {'узлов решётки':>14s} {'заполнено':>10s}")
def grid_stats(words,L):
    sub=[w for w in words if len(w)==L]
    if len(sub)<40: return None
    A=[sorted({w[i] for w in sub}) for i in range(L)]
    size=1
    for a in A: size*=len(a)
    return sub,A,size,len(sub)/size
for nm,W in [("Войнич, ядра",CORES_V),("латынь, ядра",CORES_L),("перемешка, ядра",CORES_SH)]:
    for L in (3,4,5):
        g=grid_stats(W,L)
        if not g: continue
        sub,A,size,fill=g
        print(f"  {nm:>22s} {L:6d} {len(sub):6d} {'×'.join(str(len(a)) for a in A):>24s} {size:14,d} {fill:10.1%}")
print("\n"+"="*112); print("ПРОВЕРКА НА ПЕРЕОБУЧЕНИЕ: решётка строится на ПОЛОВИНЕ ядер, покрытие меряется на ВТОРОЙ"); print("="*112)
print(f"  {'набор':>22s} {'длина':>6s} {'обучение':>9s} {'контроль':>9s} {'покрыто отложенных':>19s} {'узлов':>12s}")
def holdout(words,L,B=25):
    sub=[w for w in words if len(w)==L]
    if len(sub)<80: return None
    cov=[];sz=[]
    for b in range(B):
        rnd=random.Random(900+b); sh=sub[:]; rnd.shuffle(sh)
        h=len(sh)//2; tr,te=sh[:h],sh[h:]
        A=[set(w[i] for w in tr) for i in range(L)]
        size=1
        for a in A: size*=len(a)
        cov.append(sum(1 for w in te if all(w[i] in A[i] for i in range(L)))/len(te)); sz.append(size)
    return len(sub)//2, len(sub)-len(sub)//2, st.mean(cov), st.mean(sz)
for nm,W in [("Войнич, ядра",CORES_V),("латынь, ядра",CORES_L),("перемешка, ядра",CORES_SH)]:
    for L in (3,4,5):
        h=holdout(W,L)
        if not h: continue
        ntr,nte,cov,size=h
        print(f"  {nm:>22s} {L:6d} {ntr:9d} {nte:9d} {cov:19.1%} {size:12,.0f}")
print("\n  Смысл: высокое покрытие отложенной половины = решётка ОБОБЩАЕТ, а не пересказывает данные.")
print("  Низкое = позиционных алфавитов недостаточно, у словаря есть структура помимо позиции.")
