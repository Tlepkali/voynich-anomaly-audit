# -*- coding: utf-8 -*-
import json, collections, random, math, os
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]
LENS=[len(l) for l in VL]
def cut(ws):
    out=[];k=0
    for n in LENS:
        if k+n>len(ws): break
        out.append(ws[k:k+n]); k+=n
    return out
def MI(pairs):
    j=collections.Counter(pairs); a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
    n=len(pairs); return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
def junc(L, R=30, seed=2):
    flat=[w for l in L for w in l]; ln=[len(x) for x in L]
    def pr(seq,k):
        o=[];i=0
        for n in ln:
            s=seq[i:i+n]; i+=n
            for x,y in zip(s,s[1:]): o.append((x[-k:],y[:k]))
        return o
    o1,o3=MI(pr(flat,1)),MI(pr(flat,3))
    rnd=random.Random(seed); s1=s3=0.0
    for _ in range(R):
        sh=flat[:]; rnd.shuffle(sh); s1+=MI(pr(sh,1))/R; s3+=MI(pr(sh,3))/R
    e1,e3=o1-s1,o3-s3
    return e1,e3,e3/e1 if e1>1e-9 else float('inf')
NB=[l.split() for l in open("../naibbe/encrypted/nathist_output_ciphertext.txt").read().split("\n")]
NB=[l for l in NB if len(l)>=3]
C=[("Войнич",VL),("Naibbe",cut([w for l in NB for w in l]))]
for tag,lab in (("latin","латынь"),("english","английский"),("wiki_de","немецкий"),
                ("wiki_it","итальянский"),("wiki_el","греческий")):
    p=f"ref/{tag}.clean"
    if os.path.exists(p):
        r=cut(open(p).read().split())
        if len(r)>len(LENS)*0.6: C.append((lab,r))
print("="*104)
print("ОТНОШЕНИЕ СТЫКА НА ПОЛНОМ ОБЪЁМЕ — та же выборка у всех, 30 перемешиваний")
print("="*104)
print(f"  {'корпус':>14s} {'строк':>7s} {'слов':>8s} {'по 1 знаку':>12s} {'по 3 знакам':>13s} {'отношение':>11s}")
res=[]
for lab,L in C:
    n=sum(len(x) for x in L)
    e1,e3,r=junc(L)
    res.append((r,lab,len(L),n,e1,e3))
for r,lab,nl,n,e1,e3 in sorted(res):
    mk="  ←" if lab=="Войнич" else ""
    print(f"  {lab:>14s} {nl:7d} {n:8,d} {e1:12.4f} {e3:13.4f} {r:10.2f}×{mk}")
print("\n  ВАЖНО: на выборке 6 000 слов у Войнича выходило 0,30×, у латыни 6,5×.")
print("  Оценка по трёхзначным хвостам смещена на малых выборках — сравнивать только при равном объёме.")
