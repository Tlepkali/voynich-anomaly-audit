# -*- coding: utf-8 -*-
import json, collections, random, sys, statistics as st, os
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
    return dict(ml=m['mean_len'],ty=len(set(f)),ttr=m['ttr'],hx=m['hapax'],sl=m['mi_pos'],slm=m['mi_pos_merged'],h2m=m['h2_merged'],
                h2=m['h2'],ed1=m['ed1'],zipf=m['zipf'],adj=lineadj(L))
Vw=[w for l in VL for w in l]; T=prof(cutl(Vw))
S1=["","","","q","o","y","d","s","l","r","ch","sh","cth","ckh","cph","qo","ok","ot","yk","yt","da","che","she","qok","cho","sho","kai","dai"]
S2=["o","e","a","ee","eo","ea","ai","aii","oe","ao","ey","eee"]
S3=["","","l","r","y","n","dy","in","iin","ain","m","al","ar","or","ol","edy","eey","aiin","am","ody","eedy","chy","od"]
SLOT=[S1,S2,S3]
GL=sorted({c for s in SLOT for x in s for c in x})
def dist(a,b): return sum(1 for x,y in zip(a,b) if x!=y)+abs(len(a)-len(b))
# ЗАФИКСИРОВАННЫЕ параметры лучшей сборки — ничего не подбираем
PN,NN,NC,LOC,DR,PC,KA,PI = 0.25,3,400,8,200,0.9,500,0.15
def build(words, seed):
    rnd=random.Random(seed)
    cnt=collections.Counter(words); core={w for w,_ in cnt.most_common(NC)}
    tab={}; out=[]; act=None; nulls=None; last=""
    for j,w in enumerate(words):
        if j%DR==0:
            r=random.Random(seed*7919+j//DR)
            act=[r.sample(S,min(LOC,len(S))) for S in SLOT]
            nulls=[x for x in ("".join(a[r.randrange(len(a))] for a in act) for _ in range(NN)) if x] or ["ol"]
        if w in core:
            if w not in tab:
                r=random.Random(hash(w)%10**7)
                tab[w]="".join(s[r.randrange(len(s))] for s in SLOT) or "or"
            f=tab[w]
        else:
            if w not in tab:
                r=random.Random(hash(w)%10**7)
                base=[s[r.randrange(len(s))] for s in SLOT]; v=set()
                for _ in range(KA):
                    if r.random()<PI: v.add("".join(r.choice(GL) for _ in range(r.randint(3,6))))
                    else:
                        bb=base[:]; k=r.randrange(3); bb[k]=SLOT[k][r.randrange(len(SLOT[k]))]; v.add("".join(bb))
                tab[w]=sorted(x for x in v if x) or ["ar"]
            V=tab[w]
            f=min(V,key=lambda x:(dist(x,last),x)) if (last and rnd.random()<PC) else rnd.choice(V)
        out.append(f); last=f
        while rnd.random()<PN:
            nn=min(nulls,key=lambda x:(dist(x,last),x)) if (rnd.random()<PC and last) else rnd.choice(nulls)
            out.append(nn); last=nn
    return cutl(out)
print("="*140)
print("ПРОВЕРКА НА ПОДГОНКУ: те же параметры, другие открытые тексты и другие зёрна. Ничего не настраивается.")
print("="*140)
print(f"  {'открытый текст':>26s} {'ср.дл':>6s} {'типов':>6s} {'TTR':>6s} {'хапакс':>7s} {'слот.скл':>9s} {'h2 скл':>7s} {'ed1':>6s} {'Ципф':>6s} {'сосед':>7s}")
print(f"  {'ЦЕЛЬ — Войнич':>26s} {T['ml']:6.2f} {T['ty']:6d} {T['ttr']:6.3f} {T['hx']:7.3f} {T['slm']:9.3f} {T['h2m']:7.2f} {T['ed1']:6.3f} {T['zipf']:6.2f} {T['adj']:6.2f}×")
SRC=[("латынь (настроено на ней)","ref/latin.clean",5),("латынь, другое зерно","ref/latin.clean",77),
     ("латынь, третье зерно","ref/latin.clean",909),("английский","ref/english.clean",5),
     ("немецкий","ref/wiki_de.clean",5),("итальянский","ref/wiki_it.clean",5),
     ("греческий","ref/wiki_el.clean",5),("чешский","ref/wiki_cs.clean",5)]
for lab,path,sd in SRC:
    if not os.path.exists(path): continue
    L=build(open(path).read().split(), sd)
    if not L: 
        print(f"  {lab:>26s}  корпус мал"); continue
    p=prof(L)
    print(f"  {lab:>26s} {p['ml']:6.2f} {p['ty']:6d} {p['ttr']:6.3f} {p['hx']:7.3f} {p['slm']:9.3f} {p['h2m']:7.2f} {p['ed1']:6.3f} {p['zipf']:6.2f} {p['adj']:6.2f}×")
