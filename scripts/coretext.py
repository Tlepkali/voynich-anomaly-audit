# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys, math
sys.path.insert(0,"scripts"); import metrics
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]
VOY=[w for l in VL for w in l]
def affixes(types,k):
    pre=collections.Counter(); suf=collections.Counter()
    for w in types:
        for L in (1,2,3):
            if len(w)>L: pre[w[:L]]+=1; suf[w[-L:]]+=1
    return [a for a,_ in pre.most_common(k)],[a for a,_ in suf.most_common(k)]
def build_map(types,k):
    S=set(types); P,U=affixes(S,k); der={}
    for w in sorted(S,key=len):
        for a in P:
            if w.startswith(a) and w[len(a):] in S and len(w[len(a):])>=2: der[w]=w[len(a):]; break
        if w in der: continue
        for a in U:
            if w.endswith(a) and w[:-len(a)] in S and len(w[:-len(a)])>=2: der[w]=w[:-len(a)]; break
    root={}
    for w in S:
        x=w; seen=set()
        while x in der and x not in seen: seen.add(x); x=der[x]
        root[w]=x
    return root, len(der)/len(S)
def fit_k(types, target=0.59, ks=(5,8,12,15,20,30,45,70,110,170,260,400)):
    best=None
    for k in ks:
        r,frac=build_map(types,k)
        if best is None or abs(frac-target)<abs(best[2]-target): best=(r,k,frac)
    return best
def rewrite(lines, root): return [[root.get(w,w) for w in l] for l in lines]
def near(a,b):
    if a==b: return True
    la,lb=len(a),len(b)
    if abs(la-lb)>1: return False
    if la==lb:
        d=0
        for x,y in zip(a,b):
            if x!=y:
                d+=1
                if d>1: return False
        return d==1
    s_,l_=(a,b) if la<lb else (b,a)
    return any(l_[:i]+l_[i+1:]==s_ for i in range(len(l_)))
def MI(pairs):
    j=collections.Counter(pairs); a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
    n=len(pairs); return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
def junction(L,seed=9):
    def pr(LL,k): return [(x[-k:],y[:k]) for l in LL for x,y in zip(l,l[1:])]
    o1,o3=MI(pr(L,1)),MI(pr(L,3)); flat=[w for l in L for w in l]
    rnd=random.Random(seed); s1=s3=0.0
    for _ in range(5):
        sh=flat[:]; rnd.shuffle(sh); i=0; SH=[]
        for l in L: SH.append(sh[i:i+len(l)]); i+=len(l)
        s1+=MI(pr(SH,1))/5; s3+=MI(pr(SH,3))/5
    e1,e3=o1-s1,o3-s3
    return e1,e3,e3/max(e1,1e-9)
def adjr(L,pred,B=8,seed=3):
    o=sum(1 for l in L for i in range(len(l)-1) if pred(l[i],l[i+1]))
    rnd=random.Random(seed); acc=0.0
    for _ in range(B):
        for l in L:
            p=rnd.sample(l,len(l)); acc+=sum(1 for a,b in zip(p,p[1:]) if pred(a,b))/B
    return o/max(acc,.01)
def batt(L,lab):
    f=[w for l in L for w in l]; m=metrics.all_metrics(f,L)
    e1,e3,r=junction(L)
    return dict(lab=lab,n=len(f),ty=len(set(f)),ttr=m['ttr'],hx=m['hapax'],ml=m['mean_len'],
                h2=m['h2'],mi=m['mi_pos'],j1=e1,j3=e3,jr=r,
                same=adjr(L,lambda a,b:a==b), nearr=adjr(L,near))
def show(rows,title):
    print("\n"+"="*126); print(title); print("="*126)
    print(f"  {'вариант':>30s} {'слов':>6s} {'типов':>6s} {'TTR':>6s} {'хапакс':>7s} {'длина':>6s} {'h2':>5s} {'слотов':>7s} "
          f"{'стык1':>6s} {'стык3':>6s} {'стык3/1':>8s} {'одинак':>7s} {'похожие':>8s}")
    for d in rows:
        print(f"  {d['lab']:>30s} {d['n']:6d} {d['ty']:6d} {d['ttr']:6.3f} {d['hx']:7.3f} {d['ml']:6.2f} {d['h2']:5.2f} {d['mi']:7.3f} "
              f"{d['j1']:6.3f} {d['j3']:6.3f} {d['jr']:7.2f}× {d['same']:6.2f}× {d['nearr']:7.2f}×")
root,frac=build_map(set(VOY),15)
CV=rewrite(VL,root)
rows=[batt(VL,"Войнич, как есть"), batt(CV,f"Войнич В ЯДРАХ ({frac:.0%} выведено)")]
LAT=None
p="ref/latin.clean"
if os.path.exists(p):
    lw=open(p).read().split()
    LL=[];k=0
    for l in VL:
        if k+len(l)>len(lw): break
        LL.append(lw[k:k+len(l)]); k+=len(l)
    r2,k2,f2=fit_k(set(w for l in LL for w in l))
    rows.append(batt(LL,"латынь, как есть"))
    rows.append(batt(rewrite(LL,r2),f"латынь В ЯДРАХ ({f2:.0%}, k={k2})"))
show(rows,"БАТАРЕЯ НА ИСХОДНОМ ТЕКСТЕ И НА ПЕРЕПИСАННОМ В ЯДРАХ (доля вывода у латыни подогнана под 59 %)")
print("\n  СДВИГИ (ядра минус исходник):")
print(f"  {'корпус':>10s} {'TTR':>8s} {'хапакс':>8s} {'длина':>8s} {'h2':>7s} {'слотов':>8s} {'стык3/1':>9s} {'одинак':>8s} {'похожие':>8s}")
for i in (0,2):
    if i+1>=len(rows): break
    a,b=rows[i],rows[i+1]; nm="Войнич" if i==0 else "латынь"
    print(f"  {nm:>10s} {b['ttr']-a['ttr']:+8.3f} {b['hx']-a['hx']:+8.3f} {b['ml']-a['ml']:+8.2f} {b['h2']-a['h2']:+7.2f} "
          f"{b['mi']-a['mi']:+8.3f} {b['jr']-a['jr']:+8.2f}× {b['same']-a['same']:+7.2f}× {b['nearr']-a['nearr']:+7.2f}×")
