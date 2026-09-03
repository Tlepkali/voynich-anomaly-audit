# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VOY=[w for l in VL for w in l]
MULTI=["cth","cph","ckh","cfh","ch","sh","ee"]
CORE=set("tpkf")|{"cth","cph","ckh","cfh"}; MANTLE={"ch","sh","ee"}; CRUST=set("dlrsnxmg")
def toks(w):
    out=[];i=0
    while i<len(w):
        for m in MULTI:
            if w.startswith(m,i): out.append(m); i+=len(m); break
        else: out.append(w[i]); i+=1
    return out
def cl(t): return 3 if t in CORE else (2 if t in MANTLE else (1 if t in CRUST else 0))
def ok(seq):
    top=max(seq); k=seq.index(top)
    return all(seq[i]<=seq[i+1] for i in range(k)) and all(seq[i]>=seq[i+1] for i in range(k,len(seq)-1))
def bykl(items, seed=None):
    rnd=random.Random(seed); g=collections.defaultdict(lambda:[0,0])
    for w in items:
        c=[cl(t) for t in toks(w) if cl(t)>0]
        if len(c)<2: continue
        if seed is not None: rnd.shuffle(c)
        k=min(len(c),6); g[k][1]+=1; g[k][0]+=ok(c)
    return g
print("="*104); print("ГДЕ У МЕРЫ ЕСТЬ РАЗРЕШЕНИЕ: доля вложенных по числу классифицированных знаков в слове"); print("="*104)
T=sorted(set(VOY))
obs=bykl(T); nul=[bykl(T,s) for s in range(20)]
print(f"  {'знаков':>7s} {'типов':>7s} {'вложено':>9s} {'перемешано':>11s} {'отношение':>10s}")
for k in sorted(obs):
    a,b=obs[k]
    sh=st.mean(n[k][0]/max(n[k][1],1) for n in nul if k in n)
    lab=f"{k}" if k<6 else "6+"
    print(f"  {lab:>7s} {b:7,d} {a/b:9.1%} {sh:11.1%} {a/b/max(sh,1e-9):9.2f}×")
print("\n  ТО ЖЕ НА ЯЗЫКАХ (те же классы знаков):")
print(f"  {'корпус':>13s} {'знаков':>7s} {'типов':>7s} {'вложено':>9s} {'перемеш.':>10s} {'отнош.':>8s}")
for nm,fn in [("латынь","latin"),("английский","english"),("итальянский","wiki_it")]:
    p="ref/%s.clean"%fn
    if not os.path.exists(p): continue
    ws=sorted(set(open(p).read().split()[:60000]))
    o2=bykl(ws); n2=[bykl(ws,s) for s in range(5)]
    for k in sorted(o2):
        if k<4 or o2[k][1]<200: continue
        a,b=o2[k]; sh=st.mean(n[k][0]/max(n[k][1],1) for n in n2 if k in n)
        lab=f"{k}" if k<6 else "6+"
        print(f"  {nm:>13s} {lab:>7s} {b:7,d} {a/b:9.1%} {sh:10.1%} {a/b/max(sh,1e-9):7.2f}×")
print("\n"+"="*104); print("ТОКЕНЫ ПРОТИВ ТИПОВ: конформны ли частые слова сильнее (все слова с ≥4 классифицированными)"); print("="*104)
def rate4(items, seed=None):
    rnd=random.Random(seed); a=b=0
    for w in items:
        c=[cl(t) for t in toks(w) if cl(t)>0]
        if len(c)<4: continue
        if seed is not None: rnd.shuffle(c)
        b+=1; a+=ok(c)
    return a/max(b,1), b
ot,nt=rate4(T); st_=st.mean(rate4(T,s)[0] for s in range(20))
ok_,nk=rate4(VOY); sk=st.mean(rate4(VOY,s)[0] for s in range(20))
print(f"  типы  : {nt:6,d} слов, вложено {ot:6.1%}, перемешано {st_:6.1%}, отношение {ot/st_:5.2f}×")
print(f"  токены: {nk:6,d} слов, вложено {ok_:6.1%}, перемешано {sk:6.1%}, отношение {ok_/sk:5.2f}×")
