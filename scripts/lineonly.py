# -*- coding: utf-8 -*-
import json, collections, random, math, os
D=json.load(open("parsed.json"))
LN=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
LN=[l for l in LN if len(l)>=2]
flat=[w for l in LN for w in l]
first=set(); pos=collections.defaultdict(lambda:[0,0])   # [всего, из них первых]
for l in LN:
    for i,w in enumerate(l):
        pos[w][0]+=1
        if i==0: pos[w][1]+=1
p_first=sum(1 for l in LN)/len(flat)
print("="*98)
print("СЛОВА, ВСТРЕЧАЮЩИЕСЯ ТОЛЬКО В НАЧАЛАХ СТРОК")
print("="*98)
print(f"  строк {len(LN):,}, слов {len(flat):,}; доля первых слов среди всех: {p_first:.1%}")
only=[w for w,(n,f) in pos.items() if n==f]
print(f"  слов только-в-началах: {len(only):,}")
byn=collections.Counter(pos[w][0] for w in only)
print(f"  из них встречаются 1 раз: {byn[1]:,} ({byn[1]/len(only):.0%})")
print(f"\n  {'частота':>8s} {'таких слов':>11s} {'ТОЛЬКО первые':>14s} {'ожидание p^n':>13s} {'превышение':>11s}")
allby=collections.Counter(n for w,(n,f) in pos.items())
for n in (1,2,3,4,5,6):
    tot=allby.get(n,0)
    obs=byn.get(n,0)
    exp=tot*(p_first**n)
    r=f"{obs/exp:10.2f}×" if exp>=0.5 else "         —"
    print(f"  {n:>8d} {tot:11d} {obs:14d} {exp:13.1f} {r}")
print("\n  ожидание = сколько слов частоты n оказались бы «только первыми» случайно")
# и то же перемешиванием
rnd=random.Random(4)
def shuffled_count(R=6):
    acc=collections.Counter()
    for _ in range(R):
        sh=flat[:]; rnd.shuffle(sh)
        k=0; pp=collections.defaultdict(lambda:[0,0])
        for l in LN:
            for i in range(len(l)):
                w=sh[k]; k+=1
                pp[w][0]+=1
                if i==0: pp[w][1]+=1
        for w,(a,b) in pp.items():
            if a==b: acc[a]+=1/R
    return acc
sc=shuffled_count()
print(f"\n  {'частота':>8s} {'наблюдается':>12s} {'при перемешивании':>19s} {'превышение':>11s}")
for n in (1,2,3,4,5):
    o=byn.get(n,0); e=sc.get(n,0)
    r=f"{o/e:10.2f}×" if e>=0.5 else "         —"
    print(f"  {n:>8d} {o:12d} {e:19.1f} {r}")
print("\n" + "="*98); print("ТО ЖЕ НА ЯЗЫКАХ (нарезка строками рукописи)"); print("="*98)
sizes=[len(l) for l in LN]
def analyse(words, lab):
    L=[];k=0
    for s in sizes:
        if k+s>len(words): break
        L.append(words[k:k+s]); k+=s
    pp=collections.defaultdict(lambda:[0,0])
    for l in L:
        for i,w in enumerate(l):
            pp[w][0]+=1
            if i==0: pp[w][1]+=1
    fl=[w for l in L for w in l]
    pf=len(L)/len(fl)
    on=[w for w,(a,b) in pp.items() if a==b]
    ge2=[w for w in on if pp[w][0]>=2]
    tot2=sum(1 for w,(a,b) in pp.items() if a>=2)
    exp2=sum(pf**pp[w][0] for w,(a,b) in pp.items() if a>=2)
    return lab, len(on), len(ge2), tot2, exp2, len(ge2)/exp2 if exp2>0.5 else 0
print(f"  {'корпус':>14s} {'только первых':>14s} {'из них ≥2 раз':>14s} {'ожидание':>10s} {'превышение':>11s}")
rows=[analyse(flat,"Войнич")]
for tag,lab in (("latin","латынь"),("english","английский"),("wiki_de","немецкий")):
    p=f"ref/{tag}.clean"
    if os.path.exists(p): rows.append(analyse(open(p).read().split(),lab))
for lab,a,b,t,e,r in rows:
    mk="  ←" if lab=="Войнич" else ""
    print(f"  {lab:>14s} {a:14d} {b:14d} {e:10.1f} {r:10.2f}×{mk}")
