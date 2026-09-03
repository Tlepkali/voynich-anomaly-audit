# -*- coding: utf-8 -*-
import json, collections, random, sys, statistics as st
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]
LENS=[];tot=0
for l in VL:
    if tot>=12000: break
    LENS.append(len(l)); tot+=len(l)
def cutl(u):
    out=[];k=0
    for n in LENS:
        if k+n>len(u): return None
        out.append(u[k:k+n]); k+=n
    return out
def lineadj(L):
    obs=sum(1 for l in L for i in range(len(l)-1) if l[i]==l[i+1])
    rnd=random.Random(2); acc=0.0
    for _ in range(8):
        for l in L:
            p=rnd.sample(l,len(l)); acc+=sum(1 for a,b in zip(p,p[1:]) if a==b)/8
    return obs/max(acc,0.01)
def prof(L):
    f=[x for l in L for x in l]; m=metrics.all_metrics(f,L)
    return dict(ml=m['mean_len'],ty=len(set(f)),ttr=m['ttr'],hx=m['hapax'],
                slm=m['mi_pos_merged'],h2m=m['h2_merged'],ed1=m['ed1'],zipf=m['zipf'],adj=lineadj(L))
Vw=[w for l in VL for w in l]; T=prof(cutl(Vw))
words=open("ref/latin.clean").read().split()
# ПЕРЕСЕКАЮЩИЕСЯ наборы: один и тот же знак может стоять в разных позициях
HEAD=["q","o","y","d","s","l","r","ch","sh","cth","ckh","qo","ok","ot","yk","da","che","she","cho"]
MID =["o","e","a","ee","eo","ea","ai","aii","oe","ao","ey","ch","sh","k","t","d","l","r"]
TAIL=["l","r","y","n","dy","in","iin","ain","m","al","ar","or","ol","edy","eey","aiin","am","od","o","e","a"]
POOLS=[HEAD,MID,TAIL]
GL=sorted({c for P in POOLS for x in P for c in x})
def dist(a,b): return sum(1 for x,y in zip(a,b) if x!=y)+abs(len(a)-len(b))
def form(r, act, nslots):
    return "".join(act[i%3][r.randrange(len(act[i%3]))] for i in range(nslots))
def build(words, pn, nc, loc, dr, pc, ka, pirr, p2, p4, seed=5):
    rnd=random.Random(seed)
    cnt=collections.Counter(words); core={w for w,_ in cnt.most_common(nc)}
    tab={}; out=[]; act=None; nulls=None; last=""
    def nsl(r):
        u=r.random()
        return 2 if u<p2 else (4 if u>1-p4 else 3)
    for j,w in enumerate(words):
        if j%dr==0:
            r=random.Random(seed*7919+j//dr)
            act=[r.sample(P,min(loc,len(P))) for P in POOLS]
            nulls=[x for x in (form(r,act,nsl(r)) for _ in range(3)) if x] or ["ol"]
        if w in core:
            if w not in tab:
                r=random.Random(hash(w)%10**7)
                tab[w]=form(r,POOLS,nsl(r)) or "or"
            f=tab[w]
        else:
            if w not in tab:
                r=random.Random(hash(w)%10**7)
                k=nsl(r); base=[POOLS[i%3][r.randrange(len(POOLS[i%3]))] for i in range(k)]
                v=set()
                for _ in range(ka):
                    if r.random()<pirr: v.add("".join(r.choice(GL) for _ in range(r.randint(3,6))))
                    else:
                        bb=base[:]; q=r.randrange(k); bb[q]=POOLS[q%3][r.randrange(len(POOLS[q%3]))]
                        v.add("".join(bb))
                tab[w]=sorted(x for x in v if x) or ["ar"]
            V=tab[w]
            f=min(V,key=lambda x:(dist(x,last),x)) if (last and rnd.random()<pc) else rnd.choice(V)
        out.append(f); last=f
        while rnd.random()<pn:
            nn=min(nulls,key=lambda x:(dist(x,last),x)) if (rnd.random()<pc and last) else rnd.choice(nulls)
            out.append(nn); last=nn
    return cutl(out)
KEYS=[("ttr",1.0),("hx",1.4),("adj",1.0),("zipf",1.0),("slm",1.2),("h2m",1.0),("ed1",1.2),("ml",1.2)]
def score(p): return sum(w*abs(p[k]-T[k])/max(abs(T[k]),1e-6) for k,w in KEYS)
print("="*146)
print("ПЕРЕМЕННОЕ ЧИСЛО ЯЧЕЕК + ПЕРЕСЕКАЮЩИЕСЯ НАБОРЫ (знак может стоять в разных позициях)")
print("="*146)
res=[]
for p2 in (0.15,0.35,0.55):
    for p4 in (0.05,0.15):
        for loc in (8,12):
            for ka in (300,600):
                L=build(words,0.25,400,loc,200,0.9,ka,0.15,p2,p4)
                if not L: continue
                p=prof(L); res.append((score(p),p2,p4,loc,ka,p))
res.sort(key=lambda x:x[0])
print(f"  {'p2':>5s} {'p4':>5s} {'окно':>5s} {'вар':>5s} | {'ср.дл':>6s} {'типов':>6s} {'TTR':>6s} {'хапакс':>7s} {'слот.скл':>9s} {'h2скл':>6s} {'ed1':>6s} {'Ципф':>6s} {'сосед':>7s} | {'ошиб':>6s}")
print(f"  {'ЦЕЛЬ':>5s} {'':>5s} {'':>5s} {'':>5s} | {T['ml']:6.2f} {T['ty']:6d} {T['ttr']:6.3f} {T['hx']:7.3f} {T['slm']:9.3f} {T['h2m']:6.2f} {T['ed1']:6.3f} {T['zipf']:6.2f} {T['adj']:6.2f}× |")
for s,p2,p4,loc,ka,p in res[:9]:
    print(f"  {p2:5.2f} {p4:5.2f} {loc:5d} {ka:5d} | {p['ml']:6.2f} {p['ty']:6d} {p['ttr']:6.3f} {p['hx']:7.3f} {p['slm']:9.3f} {p['h2m']:6.2f} {p['ed1']:6.3f} {p['zipf']:6.2f} {p['adj']:6.2f}× | {s:6.3f}")
