# -*- coding: utf-8 -*-
import json, collections, math, random, glob, re, os, statistics as st
GB="naibbe/figure_utils/gaskell_bowern_2022/data"
D=json.load(open("parsed.json"))
VOY=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VOY=[l for l in VOY if len(l)>=2]
def load_lines(path, lower=True):
    t=open(path,encoding="utf-8",errors="ignore").read()
    out=[]
    for l in t.split("\n"):
        l=re.sub(r"[^A-Za-zÀ-ÿ' ]"," ",l)
        ws=[w.strip("'").lower() for w in l.split() if len(w.strip("'"))>0]
        if len(ws)>=2: out.append(ws)
    return out
GIB=[load_lines(f) for f in sorted(glob.glob(GB+"/gibberish_transcriptions/*.txt"))]
GIB=[s for s in GIB if sum(len(l) for l in s)>=80]
def cut_like(words, lens):
    out=[];k=0
    for n in lens:
        if k+n>len(words): break
        out.append(words[k:k+n]); k+=n
    return out
VLENS=[len(l) for l in VOY]
def adj(samples):
    """соседние повторы против перемешивания внутри строки; samples = список списков строк"""
    obs=0; opp=0
    for s in samples:
        for l in s: obs+=sum(1 for i in range(len(l)-1) if l[i]==l[i+1])
    rnd=random.Random(4); sims=[]
    for _ in range(300):
        tot=0
        for s in samples:
            for l in s:
                p=rnd.sample(l,len(l)); tot+=sum(1 for a,b in zip(p,p[1:]) if a==b)
        sims.append(tot)
    sims.sort(); m=sum(sims)/len(sims)
    return obs, m, obs/max(m,.01), obs/max(sims[-8],.01), obs/max(sims[7],.01)
def acf1(samples):
    xs=[];ys=[]
    for s in samples:
        for l in s:
            L=[len(w) for w in l]
            for i in range(len(L)-1): xs.append(L[i]); ys.append(L[i+1])
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    num=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
    den=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    r=num/den; se=1/math.sqrt(len(xs))
    return r, r-1.96*se, r+1.96*se, len(xs)
def MI(pairs):
    j=collections.Counter(pairs); a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
    n=len(pairs); return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
def junc(samples, R=25):
    def pairs(sm,k):
        o=[]
        for s in sm:
            for l in s:
                for x,y in zip(l,l[1:]): o.append((x[-k:],y[:k]))
        return o
    o1,o3=MI(pairs(samples,1)),MI(pairs(samples,3))
    rnd=random.Random(6); s1=s3=0.0
    flat=[w for s in samples for l in s for w in l]
    shapes=[[len(l) for l in s] for s in samples]
    for _ in range(R):
        sh=flat[:]; rnd.shuffle(sh); i=0; rs=[]
        for shp in shapes:
            s=[]
            for n in shp: s.append(sh[i:i+n]); i+=n
            rs.append(s)
        s1+=MI(pairs(rs,1))/R; s3+=MI(pairs(rs,3))/R
    return o1-s1, o3-s3
def vocab(samples):
    f=[w for s in samples for l in s for w in l]
    c=collections.Counter(f)
    hap=sum(1 for v in c.values() if v==1)/len(c)
    fr=sorted(c.values(),reverse=True)[:1000]
    xs=[math.log(i+1) for i in range(len(fr))]; ys=[math.log(v) for v in fr]
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    z=sum((a-mx)*(b-my) for a,b in zip(xs,ys))/sum((a-mx)**2 for a in xs)
    return len(c)/len(f), hap, z, len(f)
CORP={}
CORP["Войнич"]=[VOY]
CORP["БЕССМЫСЛИЦА (38 чел.)"]=GIB
for tag,lab in (("latin","латынь"),("english","английский")):
    ws=open("ref/%s.clean"%tag).read().split()
    CORP[lab]=[cut_like(ws, VLENS)]
nb=[l.split() for l in open("naibbe/encrypted/nathist_output_ciphertext.txt").read().split("\n")]
CORP["Naibbe"]=[[l for l in nb if len(l)>=2]]
print("="*112)
print("БАТАРЕЯ ПО КОРПУСУ ЧЕЛОВЕЧЕСКОЙ БЕССМЫСЛИЦЫ (Гаскелл и Боуэрн, 2022)")
print("="*112)
print(f"  {'корпус':>22s} {'слов':>8s} {'соседство':>22s} {'сцепление длин':>20s}")
res={}
for lab,S in CORP.items():
    n=sum(len(l) for s in S for l in s)
    o,m,r,lo,hi=adj(S); a,alo,ahi,np=acf1(S)
    res[lab]=(r,a)
    mark="  ←" if "БЕСС" in lab else ""
    print(f"  {lab:>22s} {n:8,d} {r:8.2f}× [{lo:.2f}–{hi:.2f}] {a:+12.3f} [{alo:+.3f}]{mark}")
print()
print(f"  {'корпус':>22s} {'стык 1 знак':>13s} {'стык 3 знака':>14s} {'TTR':>7s} {'хапаксы':>9s} {'Ципф':>7s}")
for lab,S in CORP.items():
    e1,e3=junc(S); t,h,z,n=vocab(S)
    mark="  ←" if "БЕСС" in lab else ""
    print(f"  {lab:>22s} {e1:13.4f} {e3:14.4f} {t:7.3f} {h:9.3f} {z:7.2f}{mark}")
