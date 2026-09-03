# -*- coding: utf-8 -*-
"""Держится ли результат про типы и токены вне длины 4 и вне одной транскрипции."""
import json, collections, math, random, statistics as st, os
def load(n):
    d=json.load(open(f"data/parsed_{n}.json"))
    L=[[w for w in r["words"] if '?' not in w] for r in d["rows"] if r["locus"]=="P"]
    return [l for l in L if len(l)>=3]
VL=load("ZL3b-n"); LENS=[len(l) for l in VL]
lw=open("ref/latin.clean").read().split(); LL=[];p=0
for n in LENS:
    if p+n>len(lw): break
    LL.append(lw[p:p+n]); p+=n
def mi_at(seq, n, minn=150):
    sub=[w for w in seq if len(w)==n]
    if len(sub)<minn: return float('nan'), len(sub)
    j=collections.Counter()
    for w in sub:
        for i,c in enumerate(w): j[(c,i)]+=1
    N=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (g,i),c in j.items(): pg[g]+=c; pp[i]+=c
    return sum(c/N*math.log2((c/N)/((pg[g]/N)*(pp[i]/N))) for (g,i),c in j.items()), len(sub)
def excess(seq, n, B=10, seed=50):
    o,cnt=mi_at(seq,n)
    if o!=o: return float('nan'), cnt
    v=[]
    for s in range(B):
        r=random.Random(seed+s); sh=[]
        for w in seq:
            c=list(w); r.shuffle(c); sh.append("".join(c))
        x,_=mi_at(sh,n)
        if x==x: v.append(x)
    return (o/st.mean(v) if v else float('nan')), cnt
def h2_at(seq, n, minn=150):
    sub=[w for w in seq if len(w)==n]
    if len(sub)<minn: return float('nan')
    ch=[]
    for w in sub: ch.extend(list(w))
    u=collections.Counter(ch); T=len(ch)
    h1=-sum(c/T*math.log2(c/T) for c in u.values())
    bi=collections.Counter(zip(ch,ch[1:])); M=sum(bi.values())
    return -sum(c/M*math.log2(c/M) for c in bi.values())-h1
def boot_ratio(seqV, seqL, n, fn, B=200, seed=11):
    """бутстрап по словам: отношение мера(В.)/мера(лат.)"""
    rnd=random.Random(seed); out=[]
    sv=[w for w in seqV if len(w)==n]; sl=[w for w in seqL if len(w)==n]
    if len(sv)<150 or len(sl)<150: return None
    for _ in range(B):
        a=[sv[rnd.randrange(len(sv))] for _ in range(len(sv))]
        b=[sl[rnd.randrange(len(sl))] for _ in range(len(sl))]
        x,y=fn(a,n),fn(b,n)
        if x==x and y==y and y: out.append(x/y)
    if len(out)<20: return None
    out.sort(); return st.mean(out), out[int(.025*len(out))], out[int(.975*len(out))]
print("="*104); print("РАЗРЫВ С ЛАТЫНЬЮ ПО ДЛИНАМ СЛОВА: токены против типов"); print("="*104)
tokV=[w for l in VL for w in l]; tokL=[w for l in LL for w in l]
typV=sorted(set(tokV)); typL=sorted(set(tokL))
print(f"  {'длина':>6s} {'слов В./лат.':>14s} | {'ТОКЕНЫ: В.':>11s} {'лат.':>8s} {'разрыв':>8s} | {'ТИПЫ: В.':>10s} {'лат.':>8s} {'разрыв':>8s} {'токены/типы':>12s}")
for n in (3,4,5,6,7):
    ev,cv=excess(tokV,n); el,cl=excess(tokL,n)
    tv,_=excess(typV,n); tl,_=excess(typL,n)
    if ev!=ev or el!=el or tv!=tv or tl!=tl:
        print(f"  {n:6d}   выборки мало"); continue
    gt=ev/el; gy=tv/tl
    print(f"  {n:6d} {cv:6d}/{cl:<7d} | {ev:11.1f} {el:8.1f} {gt:7.2f}× | {tv:10.1f} {tl:8.1f} {gy:7.2f}× {gt/gy:11.2f}×")
print("\n  последний столбец: во сколько раз токенный разрыв больше типового")
print("\n"+"="*104); print("h2 ПО ДЛИНАМ"); print("="*104)
print(f"  {'длина':>6s} | {'ТОКЕНЫ: В.':>11s} {'лат.':>8s} {'разрыв':>8s} | {'ТИПЫ: В.':>10s} {'лат.':>8s} {'разрыв':>8s}")
for n in (3,4,5,6,7):
    a,b=h2_at(tokV,n),h2_at(tokL,n); c,d=h2_at(typV,n),h2_at(typL,n)
    if any(x!=x for x in (a,b,c,d)): continue
    print(f"  {n:6d} | {a:11.2f} {b:8.2f} {a/b:7.2f}× | {c:10.2f} {d:8.2f} {c/d:7.2f}×")
