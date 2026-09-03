# -*- coding: utf-8 -*-
import json, collections, math, random, glob, re, os, statistics as st
GB="naibbe/figure_utils/gaskell_bowern_2022/data"
N=9900
D=json.load(open("parsed.json"))
VOY=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VOY=[l for l in VOY if len(l)>=2]
VLENS=[len(l) for l in VOY]
def norm_lines(path):
    t=open(path,encoding="utf-8",errors="ignore").read()
    out=[]
    for l in t.split("\n"):
        l=re.sub(r"[^A-Za-zÀ-ÿ'’ ]"," ",l)
        ws=[w.strip("'’").lower() for w in l.split() if w.strip("'’")]
        if len(ws)>=2: out.append(ws)
    return out
def cut(words, lens, cap):
    out=[];k=0
    for n in lens:
        if k+n>len(words) or k>=cap: break
        out.append(words[k:k+n]); k+=n
    return out
def adj(S):
    obs=sum(1 for s in S for l in s for i in range(len(l)-1) if l[i]==l[i+1])
    rnd=random.Random(4); sims=[]
    for _ in range(200):
        t=0
        for s in S:
            for l in s:
                p=rnd.sample(l,len(l)); t+=sum(1 for a,b in zip(p,p[1:]) if a==b)
        sims.append(t)
    sims.sort(); m=sum(sims)/len(sims)
    return obs/max(m,.01)
def acf_per(S):
    """по образцам: медиана и доля положительных"""
    rs=[]
    for s in S:
        xs=[];ys=[]
        for l in s:
            L=[len(w) for w in l]
            for i in range(len(L)-1): xs.append(L[i]); ys.append(L[i+1])
        if len(xs)<40: continue
        mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
        num=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
        den=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
        if den: rs.append(num/den)
    if not rs: return None,0,0
    return st.median(rs), sum(1 for x in rs if x>0), len(rs)
def MI(ps):
    j=collections.Counter(ps); a=collections.Counter(x for x,_ in ps); b=collections.Counter(y for _,y in ps)
    n=len(ps); return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
def junc(S, R=20):
    def pr(sm,k):
        return [(x[-k:],y[:k]) for s in sm for l in s for x,y in zip(l,l[1:])]
    o1,o3=MI(pr(S,1)),MI(pr(S,3))
    rnd=random.Random(6); s1=s3=0.0
    flat=[w for s in S for l in s for w in l]; shp=[[len(l) for l in s] for s in S]
    for _ in range(R):
        sh=flat[:]; rnd.shuffle(sh); i=0; rs=[]
        for sp in shp:
            q=[]
            for n_ in sp: q.append(sh[i:i+n_]); i+=n_
            rs.append(q)
        s1+=MI(pr(rs,1))/R; s3+=MI(pr(rs,3))/R
    return o1-s1, o3-s3
CORP={}
CORP["ВОЙНИЧ"]=[cut([w for l in VOY for w in l], VLENS, N)]
G=[norm_lines(f) for f in sorted(glob.glob(GB+"/gibberish_transcriptions/*.txt"))]
CORP["бессмыслица"]=[s for s in G if sum(len(l) for l in s)>=150]
for tag,lab in (("latin","латынь"),("english","английский")):
    CORP[lab]=[cut(open("ref/%s.clean"%tag).read().split(), VLENS, N)]
T=GB+"/meaningful/texts"
for f in sorted(glob.glob(T+"/Conlangs*")):
    nm=os.path.basename(f).split(" - ")[1]
    ws=[w for l in norm_lines(f) for w in l]
    if len(ws)<N: continue
    CORP.setdefault("· "+nm, [cut(ws, VLENS, N)])
print("="*104)
print("КОНЛАНГИ: та же батарея, единый объём %d слов" % N)
print("="*104)
print(f"  {'корпус':>16s} {'соседство':>11s} {'сцепление длин':>26s} {'стык 1зн':>10s} {'стык 3зн':>10s} {'отнош.':>8s}")
for lab,S in CORP.items():
    a=adj(S); m,pos,tot=acf_per(S); e1,e3=junc(S)
    acf=f"{m:+.3f} ({pos}/{tot})" if m is not None else "—"
    mk="  ←" if lab=="ВОЙНИЧ" else ""
    print(f"  {lab:>16s} {a:10.2f}× {acf:>26s} {e1:10.4f} {e3:10.4f} {e3/max(e1,1e-9):7.2f}×{mk}")
