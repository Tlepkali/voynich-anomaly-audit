# -*- coding: utf-8 -*-
import json, collections, random, math, statistics as st
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]
NB=[l.split() for l in open("../naibbe/encrypted/nathist_output_ciphertext.txt").read().split("\n")]
NB=[l for l in NB if len(l)>=3]
LENS=[len(l) for l in VL]
def cut(ws):
    out=[];k=0
    for n in LENS:
        if k+n>len(ws): break
        out.append(ws[k:k+n]); k+=n
    return out
NBc=cut([w for l in NB for w in l])
def adj_ci(L, R=400, seed=1):
    obs=sum(1 for l in L for i in range(len(l)-1) if l[i]==l[i+1])
    rnd=random.Random(seed); sims=[]
    for _ in range(R):
        s=0
        for l in L:
            p=rnd.sample(l,len(l)); s+=sum(1 for a,b in zip(p,p[1:]) if a==b)
        sims.append(s)
    sims.sort(); m=sum(sims)/R
    return obs, m, obs/m, obs/sims[-int(R*0.025)-1], obs/sims[int(R*0.025)]
def MI(pairs):
    j=collections.Counter(pairs); a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
    n=len(pairs); return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
def junc_ci(L, R=40, seed=2):
    flat=[w for l in L for w in l]; ln=[len(x) for x in L]
    def pr(seq,k):
        o=[];i=0
        for n in ln:
            s=seq[i:i+n]; i+=n
            for x,y in zip(s,s[1:]): o.append((x[-k:],y[:k]))
        return o
    o1,o3=MI(pr(flat,1)),MI(pr(flat,3))
    rnd=random.Random(seed); s1=[];s3=[]
    for _ in range(R):
        sh=flat[:]; rnd.shuffle(sh); s1.append(MI(pr(sh,1))); s3.append(MI(pr(sh,3)))
    e1=o1-sum(s1)/R; e3=o3-sum(s3)/R
    return e1,e3,e3/e1
def acf1(L):
    xs=[];ys=[]
    for l in L:
        Ls=[len(w) for w in l]
        for i in range(len(Ls)-1): xs.append(Ls[i]); ys.append(Ls[i+1])
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    num=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
    den=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    r=num/den; n=len(xs)
    se=1/math.sqrt(n)
    return r, r-1.96*se, r+1.96*se, n
print("="*92); print("ПРОВЕРКА ТРЁХ ЧИСЕЛ ДЛЯ ПИСЬМА (400 перемешиваний, 40 для стыка)"); print("="*92)
for lab,L in (("Войнич",VL),("Naibbe",NBc)):
    o,m,r,lo,hi=adj_ci(L)
    print(f"\n  {lab}")
    print(f"    соседство: набл. {o}, случайно {m:.1f} → {r:.2f}× [95 %: {lo:.2f}–{hi:.2f}]")
    e1,e3,rt=junc_ci(L)
    print(f"    стык: по 1 знаку {e1:.4f}, по 3 знакам {e3:.4f} → отношение {rt:.2f}×")
    a,alo,ahi,n=acf1(L)
    print(f"    сцепление длин: {a:+.3f} [95 %: {alo:+.3f}…{ahi:+.3f}], пар {n:,}")
