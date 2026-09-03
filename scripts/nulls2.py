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
S1=["","q","o","y","d","s","l","r","ch","sh","cth","ckh","cph","qo","ok","ot","yk","yt","da","che","she","qok","cho","sho","kai","dai"]
S2=["o","e","a","ee","eo","ea","ai","aii","oe","ao","ey","eee"]
S3=["","l","r","y","n","dy","in","iin","ain","m","al","ar","or","ol","edy","eey","aiin","am","ody","eedy","chy","od"]
SLOT=[S1,S2,S3]
def build(pnull, nnull, kalt, ncore, seed=5):
    rnd=random.Random(seed)
    cnt=collections.Counter(words); core={w for w,_ in cnt.most_common(ncore)}
    rn=random.Random(seed*31)
    nulls=["".join(s[rn.randrange(len(s))] for s in SLOT) for _ in range(nnull)]
    nset=set(nulls)
    tab={}; out=[]
    for w in words:
        if w not in tab:
            r=random.Random(hash(w)%10**7)
            base=[s[r.randrange(len(s))] for s in SLOT]
            if w in core:
                tab[w]=["".join(base)]                      # частое — одна запись
            else:
                v=set()
                for _ in range(kalt):                       # редкое — ПОХОЖИЕ варианты: меняется одна ячейка
                    b=base[:]; k=r.randrange(3); b[k]=SLOT[k][r.randrange(len(SLOT[k]))]
                    v.add("".join(b))
                tab[w]=sorted(v-nset) or ["".join(base)]
        out.append(rnd.choice(tab[w]))
        while rnd.random()<pnull: out.append(rnd.choice(nulls))
    return cutl(out)
KEYS=[("ttr",1.0),("hx",1.2),("adj",1.0),("zipf",1.0),("sl",0.8),("h2",0.6),("ed1",1.0),("ml",0.5),("cv",0.4)]
def score(p): return sum(w*abs(p[k]-T[k])/max(abs(T[k]),1e-6) for k,w in KEYS)
print("="*142)
print("ТО ЖЕ, НО ВАРИАНТЫ ПОХОЖИ: варианты написания редкого слова различаются ОДНОЙ ячейкой")
print("="*142)
res=[]
for pn in (0.25,0.4,0.55):
    for nn in (5,10,25):
        for ka in (4,12):
            for nc in (150,600,1500):
                L=build(pn,nn,ka,nc)
                if not L: continue
                p=prof(L); res.append((score(p),pn,nn,ka,nc,p))
res.sort(key=lambda x:x[0])
print(f"  {'пуст':>5s} {'набор':>6s} {'вар':>4s} {'ядро':>5s} | {'ср.дл':>6s} {'типов':>6s} {'TTR':>6s} {'хапакс':>7s} {'слотов':>7s} {'h2':>5s} {'ed1':>6s} {'Ципф':>6s} {'сосед':>7s} | {'ошиб':>6s}")
print(f"  {'ЦЕЛЬ':>5s} {'':>6s} {'':>4s} {'':>5s} | {T['ml']:6.2f} {T['ty']:6d} {T['ttr']:6.3f} {T['hx']:7.3f} {T['sl']:7.3f} {T['h2']:5.2f} {T['ed1']:6.3f} {T['zipf']:6.2f} {T['adj']:6.2f}× |")
for s,pn,nn,ka,nc,p in res[:8]:
    print(f"  {pn:5.2f} {nn:6d} {ka:4d} {nc:5d} | {p['ml']:6.2f} {p['ty']:6d} {p['ttr']:6.3f} {p['hx']:7.3f} {p['sl']:7.3f} {p['h2']:5.2f} {p['ed1']:6.3f} {p['zipf']:6.2f} {p['adj']:6.2f}× | {s:6.3f}")
