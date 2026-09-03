# -*- coding: utf-8 -*-
import json, collections, random, sys, math, statistics as st
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
words=open("ref/latin.clean").read().split()
HEAD=["q","o","y","d","s","l","r","ch","sh","cth","ckh","qo","ok","ot","yk","da","che","she","cho"]
MID =["o","e","a","ee","eo","ea","ai","aii","oe","ao","ey","ch","sh","k","t","d","l","r"]
TAIL=["l","r","y","n","dy","in","iin","ain","m","al","ar","or","ol","edy","eey","aiin","am","od","o","e","a"]
POOLS=[HEAD,MID,TAIL]; GL=sorted({c for P in POOLS for x in P for c in x})
def dist(a,b): return sum(1 for x,y in zip(a,b) if x!=y)+abs(len(a)-len(b))
def model(seed=5,pn=0.25,nc=400,loc=8,dr=200,pc=0.9,ka=300,pirr=0.15,p2=0.15,p4=0.05):
    rnd=random.Random(seed)
    cnt=collections.Counter(words); core={w for w,_ in cnt.most_common(nc)}
    tab={}; out=[]; act=None; nulls=None; last=""
    def nsl(r):
        u=r.random(); return 2 if u<p2 else (4 if u>1-p4 else 3)
    def form(r,pools,k): return "".join(pools[i%3][r.randrange(len(pools[i%3]))] for i in range(k))
    for j,w in enumerate(words):
        if j%dr==0:
            r=random.Random(seed*7919+j//dr)
            act=[r.sample(P,min(loc,len(P))) for P in POOLS]
            nulls=[x for x in (form(r,act,nsl(r)) for _ in range(3)) if x] or ["ol"]
        if w in core:
            if w not in tab:
                r=random.Random(hash(w)%10**7); tab[w]=form(r,POOLS,nsl(r)) or "or"
            f=tab[w]
        else:
            if w not in tab:
                r=random.Random(hash(w)%10**7); k=nsl(r); base=[POOLS[i%3][r.randrange(len(POOLS[i%3]))] for i in range(k)]
                v=set()
                for _ in range(ka):
                    if r.random()<pirr: v.add("".join(r.choice(GL) for _ in range(r.randint(3,6))))
                    else:
                        bb=base[:]; q=r.randrange(k); bb[q]=POOLS[q%3][r.randrange(len(POOLS[q%3]))]; v.add("".join(bb))
                tab[w]=sorted(x for x in v if x) or ["ar"]
            V=tab[w]
            f=min(V,key=lambda x:(dist(x,last),x)) if (last and rnd.random()<pc) else rnd.choice(V)
        out.append(f); last=f
        while rnd.random()<pn:
            nn=min(nulls,key=lambda x:(dist(x,last),x)) if (rnd.random()<pc and last) else rnd.choice(nulls)
            out.append(nn); last=nn
    return cutl(out)
def tmpl():   # базовая линия: простой шаблонный код 1:1
    r0=random.Random(3); pool=sorted({a+b+c for a in HEAD for b in MID for c in TAIL}); r0.shuffle(pool)
    tab={}; out=[]
    for w in words:
        if w not in tab:
            if not pool: break
            tab[w]=pool.pop()
        out.append(tab[w])
    return cutl(out)
CORP={"Войнич (цель)":cutl([w for l in VL for w in l]), "МОДЕЛЬ":model(),
      "латынь как есть":cutl(words), "простой шаблон 1:1":tmpl()}
def MI(pairs):
    j=collections.Counter(pairs); a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
    n=len(pairs); return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
rnd=random.Random(9)
print("="*112)
print("ПРОВЕРКА ВНЕ ПОДГОНКИ: пять мер, ни одна не участвовала в настройке")
print("="*112)
print(f"\n  1. АСИММЕТРИЯ СТЫКА (избыток над случайным порядком слов)")
print(f"     {'корпус':>20s} {'по 1 знаку':>12s} {'по 3 знакам':>13s} {'отношение':>11s}")
for lab,L in CORP.items():
    if not L: continue
    flat=[w for l in L for w in l]
    def pr(seq,k):
        o=[];i=0
        for n in LENS:
            s=seq[i:i+n]; i+=n
            for x,y in zip(s,s[1:]): o.append((x[-k:],y[:k]))
        return o
    o1,o3=MI(pr(flat,1)),MI(pr(flat,3)); s1=s3=0.0
    for _ in range(5):
        sh=flat[:]; rnd.shuffle(sh); s1+=MI(pr(sh,1))/5; s3+=MI(pr(sh,3))/5
    e1,e3=o1-s1,o3-s3
    mk="  ←" if lab=="МОДЕЛЬ" else ""
    print(f"     {lab:>20s} {e1:12.3f} {e3:13.3f} {e3/max(e1,1e-9):10.2f}×{mk}")
print(f"\n  2. LAAFU: расхождение первых знаков начала строки и остальных")
print(f"     {'корпус':>20s} {'line_div':>10s}")
for lab,L in CORP.items():
    if not L: continue
    m=metrics.all_metrics([w for l in L for w in l], L)
    mk="  ←" if lab=="МОДЕЛЬ" else ""
    print(f"     {lab:>20s} {m.get('line_div',0):10.3f}{mk}")
print(f"\n  3. ПРОФИЛЬ ВОЗВРАТА СЛОВА (сколько раз слово повторяется на расстоянии d)")
print(f"     {'корпус':>20s} " + " ".join(f"{'d='+str(d):>6s}" for d in range(1,7)))
for lab,L in CORP.items():
    if not L: continue
    flat=[w for l in L for w in l]; pos=collections.defaultdict(list)
    for i,w in enumerate(flat): pos[w].append(i)
    row=[sum(sum(1 for a,b in zip(v,v[1:]) if b-a==d) for v in pos.values()) for d in range(1,7)]
    mk="  ← пик на d=2?" if lab=="МОДЕЛЬ" else ""
    print(f"     {lab:>20s} " + " ".join(f"{x:6d}" for x in row) + mk)
print(f"\n  4. ХВОСТОВЫЕ КЛАССЫ: разброс доли удвоений по трёхзначному хвосту")
print(f"     {'корпус':>20s} {'классов':>8s} {'мин':>7s} {'макс':>7s} {'размах':>8s}")
for lab,L in CORP.items():
    if not L: continue
    pair=collections.Counter(); adj=collections.Counter()
    for l in L:
        for w,n in collections.Counter(l).items():
            if n>=2: pair[w]+=n-1
        for i in range(len(l)-1):
            if l[i]==l[i+1]: adj[l[i]]+=1
    g=collections.defaultdict(lambda:[0,0])
    for w,n in pair.items():
        k=w[-3:] if len(w)>=3 else w
        g[k][0]+=n; g[k][1]+=adj.get(w,0)
    big=[(v[1]/v[0],k) for k,v in g.items() if v[0]>=20]
    if len(big)<2: print(f"     {lab:>20s} {len(big):8d}      — данных мало"); continue
    big.sort()
    mk="  ←" if lab=="МОДЕЛЬ" else ""
    print(f"     {lab:>20s} {len(big):8d} {big[0][0]:6.1%} {big[-1][0]:6.1%} {big[-1][0]-big[0][0]:7.1%}{mk}")
