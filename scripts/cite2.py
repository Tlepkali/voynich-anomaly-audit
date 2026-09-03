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
    return dict(ml=m['mean_len'],cv=st.pstdev([len(w) for w in f])/m['mean_len'],ty=len(set(f)),
                ttr=m['ttr'],hx=m['hapax'],sl=m['mi_pos'],h2=m['h2'],ed1=m['ed1'],zipf=m['zipf'],adj=lineadj(L))
Vw=[w for l in VL for w in l]; T=prof(cutl(Vw))
words=open("ref/latin.clean").read().split()
# больше пустых вариантов — формы короче; часть форм нерегулярна — слотовость ниже
S1=["","","","q","o","y","d","s","l","r","ch","sh","cth","ckh","cph","qo","ok","ot","yk","yt","da","che","she","qok","cho","sho","kai","dai"]
S2=["o","e","a","ee","eo","ea","ai","aii","oe","ao","ey","eee"]
S3=["","","l","r","y","n","dy","in","iin","ain","m","al","ar","or","ol","edy","eey","aiin","am","ody","eedy","chy","od"]
SLOT=[S1,S2,S3]
GL=sorted({c for s in SLOT for x in s for c in x})
def dist(a,b): return sum(1 for x,y in zip(a,b) if x!=y)+abs(len(a)-len(b))
def build(pnull,nnull,ncore,local,drift,pcite,kalt,pirr,seed=5):
    rnd=random.Random(seed)
    cnt=collections.Counter(words); core={w for w,_ in cnt.most_common(ncore)}
    tab={}; out=[]; act=None; nulls=None; last=""
    for j,w in enumerate(words):
        if j%drift==0:
            r=random.Random(seed*7919+j//drift)
            act=[r.sample(S,min(local,len(S))) for S in SLOT]
            nulls=["".join(a[r.randrange(len(a))] for a in act) for _ in range(nnull)]
        if w in core:
            if w not in tab:
                r=random.Random(hash(w)%10**7)
                tab[w]="".join(s[r.randrange(len(s))] for s in SLOT)
            f=tab[w]
        else:
            if w not in tab:
                r=random.Random(hash(w)%10**7)
                base=[s[r.randrange(len(s))] for s in SLOT]
                v=set()
                for _ in range(kalt):
                    if r.random()<pirr:                      # нерегулярная форма — вне шаблона
                        v.add("".join(r.choice(GL) for _ in range(r.randint(3,6))))
                    else:
                        bb=base[:]; k=r.randrange(3); bb[k]=SLOT[k][r.randrange(len(SLOT[k]))]
                        v.add("".join(bb))
                tab[w]=sorted(x for x in v if x)
            V=tab[w]
            f=min(V,key=lambda x:(dist(x,last),x)) if (last and rnd.random()<pcite) else rnd.choice(V)
        out.append(f); last=f
        while rnd.random()<pnull:
            nn=min(nulls,key=lambda x:(dist(x,last),x)) if (rnd.random()<pcite and last) else rnd.choice(nulls)
            if nn: out.append(nn); last=nn
    return cutl(out)
KEYS=[("ttr",1.0),("hx",1.4),("adj",1.0),("zipf",1.0),("sl",1.0),("h2",0.6),("ed1",1.2),("ml",0.8),("cv",0.4)]
def score(p): return sum(w*abs(p[k]-T[k])/max(abs(T[k]),1e-6) for k,w in KEYS)
print("="*152)
print("ДОБОР: больше вариантов на редкое слово (хапаксы), доля нерегулярных форм (слотовость), пустые ячейки (длина)")
print("="*152)
res=[]
for ka in (60,200,500):
    for pirr in (0.0,0.15,0.35):
        for pn in (0.15,0.25):
            for nc in (100,400):
                L=build(pn,3,nc,8,200,0.9,ka,pirr)
                if not L: continue
                p=prof(L); res.append((score(p),ka,pirr,pn,nc,p))
res.sort(key=lambda x:x[0])
print(f"  {'вар':>4s} {'нерег':>6s} {'пуст':>5s} {'ядро':>5s} | {'ср.дл':>6s} {'типов':>6s} {'TTR':>6s} {'хапакс':>7s} {'слотов':>7s} {'h2':>5s} {'ed1':>6s} {'Ципф':>6s} {'сосед':>7s} | {'ошиб':>6s}")
print(f"  {'ЦЕЛЬ':>4s} {'':>6s} {'':>5s} {'':>5s} | {T['ml']:6.2f} {T['ty']:6d} {T['ttr']:6.3f} {T['hx']:7.3f} {T['sl']:7.3f} {T['h2']:5.2f} {T['ed1']:6.3f} {T['zipf']:6.2f} {T['adj']:6.2f}× |")
for s,ka,pi,pn,nc,p in res[:9]:
    print(f"  {ka:4d} {pi:6.2f} {pn:5.2f} {nc:5d} | {p['ml']:6.2f} {p['ty']:6d} {p['ttr']:6.3f} {p['hx']:7.3f} {p['sl']:7.3f} {p['h2']:5.2f} {p['ed1']:6.3f} {p['zipf']:6.2f} {p['adj']:6.2f}× | {s:6.3f}")
