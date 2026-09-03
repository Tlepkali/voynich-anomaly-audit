# -*- coding: utf-8 -*-
import json, collections, random, sys, math, statistics as st, re
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]
# строки Naibbe — как в его файле
NB=[l.split() for l in open("../naibbe/encrypted/nathist_output_ciphertext.txt").read().split("\n")]
NB=[l for l in NB if len(l)>=3]
print(f"  Войнич: {len(VL)} строк, {sum(len(l) for l in VL):,} слов")
print(f"  Naibbe: {len(NB)} строк, {sum(len(l) for l in NB):,} слов")
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
def MI(pairs):
    j=collections.Counter(pairs); a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
    n=len(pairs); return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
rnd=random.Random(9)
def junc(L):
    flat=[w for l in L for w in l]
    def pr(seq,k):
        o=[];i=0
        for n in [len(x) for x in L]:
            s=seq[i:i+n]; i+=n
            for x,y in zip(s,s[1:]): o.append((x[-k:],y[:k]))
        return o
    o1,o3=MI(pr(flat,1)),MI(pr(flat,3)); s1=s3=0.0
    for _ in range(4):
        sh=flat[:]; rnd.shuffle(sh); s1+=MI(pr(sh,1))/4; s3+=MI(pr(sh,3))/4
    return o1-s1, o3-s3
def tails(L):
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
    big=sorted((v[1]/v[0]) for k,v in g.items() if v[0]>=20)
    return (big[-1]-big[0]) if len(big)>=2 else 0.0
def full(L,lab):
    f=[w for l in L for w in l]; m=metrics.all_metrics(f,L)
    e1,e3=junc(L)
    return dict(lab=lab, ml=m['mean_len'], cv=st.pstdev([len(w) for w in f])/m['mean_len'],
                ty=len(set(f)), ttr=m['ttr'], hx=m['hapax'], slm=m['mi_pos_merged'],
                h2m=m['h2_merged'], ed1=m['ed1'], zipf=m['zipf'], adj=lineadj(L),
                e1=e1, e3=e3, ratio=e3/max(e1,1e-9), ld=m.get('line_div',0))
V=full(cutl([w for l in VL for w in l]),"Войнич")
N=full(cutl([w for l in NB for w in l]),"Naibbe")
print("\n"+"="*94); print("NAIBBE ПРОТИВ ВОЙНИЧА: та же батарея, что убила мою модель"); print("="*94)
KEYS=[("ml","средняя длина",""),("cv","СКО/среднее",""),("ty","типов",""),("ttr","TTR",""),
      ("hx","хапаксы",""),("zipf","наклон Ципфа",""),("slm","слотовость",""),("h2m","h2",""),
      ("ed1","отл. в 1 знак",""),("adj","соседство","×"),("ld","LAAFU",""),
      ("e1","стык по 1 знаку",""),("e3","стык по 3 знакам",""),("ratio","ОТНОШЕНИЕ стыка","×")]
print(f"  {'мера':>20s} {'Войнич':>10s} {'Naibbe':>10s} {'расхождение':>13s}")
for k,lab,suf in KEYS:
    a,b=V[k],N[k]
    if k=="ty": s=f"{abs(b-a)/max(abs(a),1e-9):12.0%}"
    else: s=f"{abs(b-a)/max(abs(a),1e-9):12.0%}"
    fa=f"{a:10.0f}" if k=="ty" else f"{a:10.3f}"
    fb=f"{b:10.0f}" if k=="ty" else f"{b:10.3f}"
    print(f"  {lab:>20s} {fa} {fb} {s}")
print(f"  {'разброс хвостов':>20s} {tails(cutl([w for l in VL for w in l])):10.3f} {tails(cutl([w for l in NB for w in l])):10.3f}")
