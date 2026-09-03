# -*- coding: utf-8 -*-
"""Второе разложение, устроенное ИНАЧЕ: сигнатуры Голдсмита (Linguistica).
Основа не «аффикс + слово из словаря», а группировка основ по НАБОРУ окончаний,
которые с ними встречаются. Никакой ссылки на словарь.
"""
import json, collections, random, statistics as st, math, os, sys
def signatures(types, min_stems=3, min_sufs=2, maxaff=4):
    """стем -> множество суффиксов; сигнатура = набор суффиксов, общий для >=min_stems основ"""
    stem_sufs=collections.defaultdict(set)
    for w in types:
        for i in range(2, len(w)):                 # основа не короче 2
            if len(w)-i<=maxaff: stem_sufs[w[:i]].add(w[i:])
        stem_sufs[w].add("")
    sig=collections.defaultdict(list)
    for stem,sufs in stem_sufs.items():
        if len(sufs)>=min_sufs: sig[frozenset(sufs)].append(stem)
    good={}
    for s,stems in sig.items():
        if len(stems)>=min_stems:
            for st_ in stems: good.setdefault(st_,set()).update(s)
    return good
def decompose(types, min_stems=3, min_sufs=2):
    good=signatures(types, min_stems, min_sufs)
    root={}
    for w in types:
        best=w
        for i in range(2, len(w)):
            stem, suf = w[:i], w[i:]
            if stem in good and suf in good[stem] and len(stem)<len(best): best=stem
        root[w]=best
    der=sum(1 for w in types if root[w]!=w)
    return root, der/max(len(types),1)
def nbrs(T):
    idx=collections.defaultdict(set)
    for w in T:
        idx[w].add(w)
        for i in range(len(w)): idx[w[:i]+w[i+1:]].add(w)
    nb=collections.defaultdict(set)
    for _,ws in idx.items():
        ws=list(ws)
        for i in range(len(ws)):
            for j in range(i+1,len(ws)):
                a,b=ws[i],ws[j]
                if abs(len(a)-len(b))<=1: nb[a].add(b); nb[b].add(a)
    return nb
def shape(T):
    T=set(T); nb=nbrs(T)
    def m(d):
        g=[len(nb.get(w,())) for w in T if len(w)==d]
        return st.mean(g) if len(g)>=15 else float('nan')
    a,b=m(3),m(5)
    return b/a if a==a and b==b and a>0 else float('nan')
def mi(pairs):
    j=collections.Counter(pairs); a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
    n=len(pairs); return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
def junc1(L,seed=9):
    pr=lambda LL:[(x[-1:],y[:1]) for l in LL for x,y in zip(l,l[1:])]
    o=mi(pr(L)); f=[w for l in L for w in l]; rnd=random.Random(seed); s=0.0
    for _ in range(5):
        sh=f[:]; rnd.shuffle(sh); i=0; SH=[]
        for l in L: SH.append(sh[i:i+len(l)]); i+=len(l)
        s+=mi(pr(SH))/5
    return o-s
def mi4(T):
    sub=[w for w in T if len(w)==4]
    if len(sub)<150: return float('nan')
    j=collections.Counter()
    for w in sub:
        for i,c in enumerate(w): j[(c,i)]+=1
    n=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (g,i),c in j.items(): pg[g]+=c; pp[i]+=c
    return sum(c/n*math.log2((c/n)/((pg[g]/n)*(pp[i]/n))) for (g,i),c in j.items())
def slot_exc(T,B=10):
    o=mi4(T)
    if o!=o: return float('nan')
    v=[]
    for s in range(B):
        rnd=random.Random(50+s); sh=[]
        for w in T:
            c=list(w); rnd.shuffle(c); sh.append("".join(c))
        x=mi4(sh)
        if x==x: v.append(x)
    return o/st.mean(v) if v else float('nan')
def load(n):
    d=json.load(open(f"data/parsed_{n}.json"))
    L=[[w for w in r["words"] if '?' not in w] for r in d["rows"] if r["locus"]=="P"]
    return [l for l in L if len(l)>=3]
VL=load("ZL3b-n"); LENS=[len(l) for l in VL]
lw=open("ref/latin.clean").read().split(); LL=[];p=0
for n in LENS:
    if p+n>len(lw): break
    LL.append(lw[p:p+n]); p+=n
print("="*106); print("ВТОРОЕ РАЗЛОЖЕНИЕ (сигнатуры Голдсмита) — держится ли атрибуция"); print("="*106)
print(f"  {'корпус':>10s} {'выведено':>9s} {'плотн дл5/3':>26s} {'стык 1 знак':>24s} {'слотовость (типы)':>26s}")
print(f"  {'':>10s} {'':>9s} {'все':>8s} {'ядра':>8s} {'сдвиг':>7s} {'все':>7s} {'ядра':>7s} {'сдвиг':>7s} {'все':>8s} {'ядра':>8s} {'сдвиг':>7s}")
for lab,L in [("Войнич",VL),("латынь",LL)]:
    T=sorted({w for l in L for w in l})
    root,fr=decompose(T)
    C=[[root.get(w,w) for w in l] for l in L]
    CT=sorted({w for l in C for w in l})
    s1,s2=shape(T),shape(CT); j1,j2=junc1(L),junc1(C); m1,m2=slot_exc(T),slot_exc(CT)
    f=lambda x: f"{x:8.2f}" if x==x else "       —"
    print(f"  {lab:>10s} {fr:8.1%} {f(s1)} {f(s2)} {s2-s1:+7.2f} {j1:7.3f} {j2:7.3f} {j2-j1:+7.3f} {f(m1)} {f(m2)} {m2-m1:+7.2f}")
print("\n  для сверки, ПЕРВЫЙ алгоритм (аффикс + слово из словаря):")
print("    Войнич  выведено 57,2 %  плотность 0,73→0,40 (−0,33)  стык 0,194→0,036 (−0,157)  слотовость 21,3→5,0")
print("    латынь  выведено 33 %    ")
