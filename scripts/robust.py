# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, math
NAMES=[("ZL3b-n","Зандберген–Ландини"),("IT2a-n","Такахаси"),("RF1b-e","Reference RF1b"),
       ("GC2a-n","Класton v101"),("FG2a-n","FSG"),("CD2a-n","Карриер (частичн.)")]
def load(n):
    d=json.load(open(f"data/parsed_{n}.json"))
    L=[[w for w in r["words"] if '?' not in w] for r in d["rows"] if r["locus"]=="P"]
    return [l for l in L if len(l)>=3]
def corr(P):
    xs=[a for a,_ in P]; ys=[b for _,b in P]
    mx,my=st.mean(xs),st.mean(ys)
    n=sum((a-mx)*(b-my) for a,b in zip(xs,ys)); d=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    return n/d if d else 0
def rank_corr(L):
    f=[w for l in L for w in l]; c=collections.Counter(f)
    rk={w:i+1 for i,(w,_) in enumerate(c.most_common())}
    return corr([(math.log(rk[l[i]]),math.log(rk[l[i+1]])) for l in L for i in range(len(l)-1)])
def adj_ratio(L,B=8,seed=3):
    o=sum(1 for l in L for i in range(len(l)-1) if l[i]==l[i+1])
    rnd=random.Random(seed); acc=0.0
    for _ in range(B):
        for l in L:
            p=rnd.sample(l,len(l)); acc+=sum(1 for a,b in zip(p,p[1:]) if a==b)/B
    return o/max(acc,.01)
def affixes(T,k=15):
    pre=collections.Counter(); suf=collections.Counter()
    for w in T:
        for n in (1,2,3):
            if len(w)>n: pre[w[:n]]+=1; suf[w[-n:]]+=1
    return [a for a,_ in pre.most_common(k)],[a for a,_ in suf.most_common(k)]
def decomp(T,k=15):
    S=set(T); P,U=affixes(S,k); der={}
    for w in sorted(S,key=len):
        if any(w.startswith(a) and w[len(a):] in S and len(w[len(a):])>=2 for a in P): der[w]=1; continue
        if any(w.endswith(a) and w[:-len(a)] in S and len(w[:-len(a)])>=2 for a in U): der[w]=1
    return len(der)/len(S)
def shuf_types(T,seed=0):
    rnd=random.Random(seed); out=set()
    for w in T:
        c=list(w); rnd.shuffle(c); out.add("".join(c))
    return out
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
def shape(T,d1=3,d2=5):
    T=set(T); nb=nbrs(T)
    def m(d):
        g=[len(nb.get(w,())) for w in T if len(w)==d]
        return st.mean(g) if len(g)>=15 else float('nan')
    a,b=m(d1),m(d2)
    return (b/a if a==a and b==b and a>0 else float('nan'))
def MI(pairs):
    j=collections.Counter(pairs); a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
    n=len(pairs); return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
def junc1(L,seed=9):
    pr=lambda LL:[(x[-1:],y[:1]) for l in LL for x,y in zip(l,l[1:])]
    o=MI(pr(L)); f=[w for l in L for w in l]; rnd=random.Random(seed); s=0.0
    for _ in range(5):
        sh=f[:]; rnd.shuffle(sh); i=0; SH=[]
        for l in L: SH.append(sh[i:i+len(l)]); i+=len(l)
        s+=MI(pr(SH))/5
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
def slot_excess(T,B=10):
    o=mi4(T)
    if o!=o: return float('nan')
    v=[]
    for s in range(B):
        x=mi4(shuf_types(T,50+s))
        if x==x: v.append(x)
    return o/st.mean(v) if v else float('nan')
print("="*126); print("УСТОЙЧИВОСТЬ ЯДРА РЕЗУЛЬТАТОВ ПО ШЕСТИ ТРАНСКРИПЦИЯМ"); print("="*126)
print(f"  {'транскрипция':>20s} {'токенов':>8s} {'ранг-корр':>10s} {'соседн.=':>9s} {'выводимо':>9s} "
      f"{'контроль':>9s} {'плотн дл5/3':>12s} {'стык 1зн':>9s} {'слотов ×':>9s}")
for n,lab in NAMES:
    L=load(n); T=sorted({w for l in L for w in l}); f=[w for l in L for w in l]
    dr=decomp(T); dc=decomp(sorted(shuf_types(T)))
    print(f"  {lab:>20s} {len(f):8d} {rank_corr(L):+10.4f} {adj_ratio(L):8.2f}× {dr:8.1%} "
          f"{dc:8.1%} {shape(T):12.2f} {junc1(L):9.3f} {slot_excess(T):8.2f}×")
