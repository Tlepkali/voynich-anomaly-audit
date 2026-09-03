# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os
D=json.load(open("parsed.json")); PG=D["pages"]
NAME={"H":"травник","B":"«банный»","S":"звёзды","T":"текст","P":"аптечный"}
sec=collections.defaultdict(list)
for r in D["rows"]:
    if r["locus"]!="P": continue
    m=PG.get(r["page"],{}); ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=2: sec[(m.get("I","?"),m.get("L","?"))].append((r["page"],ws))
def pool(s,L=None): return [x for (a,b),v in sec.items() if a==s and (L is None or b==L) for x in v]
def samp(ls,N,rnd):
    sh=ls[:]; rnd.shuffle(sh); f=[]
    for _,l in sh:
        f+=l
        if len(f)>=N: break
    return set(f[:N]) if len(f)>=N else None
print("="*100); print("КОНТРОЛЬ ЖАККАРА: две половины ОДНОГО раздела против разных разделов"); print("="*100)
print("  (по 1500 слов в каждой выборке, 30 повторов; половины делятся по страницам)")
def split_half(ls,N=1500,B=30):
    pgs=sorted({p for p,_ in ls}); out=[]
    for b in range(B):
        rnd=random.Random(100+b); sh=pgs[:]; rnd.shuffle(sh)
        h=set(sh[:len(sh)//2])
        A=[x for x in ls if x[0] in h]; Bs=[x for x in ls if x[0] not in h]
        a=samp(A,N,rnd); c=samp(Bs,N,rnd)
        if a and c: out.append(len(a&c)/len(a|c))
    return (st.mean(out), st.stdev(out)) if len(out)>2 else (None,None)
for s in ["S","H","B"]:
    for L in ["B","A"]:
        ls=pool(s,L); n=sum(len(l) for _,l in ls)
        if n<3200: continue
        m,sd=split_half(ls)
        if m: print(f"  внутри раздела {NAME[s]:>10s}/{L}  ({n:6,d} слов):  Жаккар {m:.3f} ± {sd:.3f}")
print()
def cross(s1,L1,s2,L2,N=1500,B=30):
    a_,b_=pool(s1,L1),pool(s2,L2); out=[]
    for i in range(B):
        rnd=random.Random(200+i); x=samp(a_,N,rnd); y=samp(b_,N,rnd)
        if x and y: out.append(len(x&y)/len(x|y))
    return st.mean(out), st.stdev(out)
for a,b in [(("S","B"),("B","B")),(("S","B"),("H","B")),(("B","B"),("H","B")),(("H","A"),("H","B")),(("H","A"),("P","A"))]:
    m,sd=cross(a[0],a[1],b[0],b[1])
    print(f"  между   {NAME[a[0]]}/{a[1]:1s} и {NAME[b[0]]}/{b[1]:1s}".ljust(40)+f":  Жаккар {m:.3f} ± {sd:.3f}")
print("\n"+"="*100); print("ЧТО ДЕРЖИТ НИЗКИЙ TTR «БАННОГО»"); print("="*100)
for s in ["B","S","H"]:
    f=[w for _,l in pool(s,"B") for w in l]; c=collections.Counter(f)
    top=c.most_common(8); cov=sum(v for _,v in top)/len(f)
    print(f"  {NAME[s]:>10s}: топ-8 покрывают {cov:5.1%} текста | "+" ".join(f"{w}·{v}" for w,v in top[:6]))
print("\n"+"="*100); print("TTR@2000 «банного» НА ФОНЕ ЕСТЕСТВЕННЫХ ЯЗЫКОВ"); print("="*100)
ref=[]
for fn in sorted(os.listdir("ref")):
    if not fn.endswith(".clean"): continue
    ws=open("ref/"+fn,encoding="utf-8",errors="ignore").read().split()
    if len(ws)<12000: continue
    v=[]
    for b in range(20):
        rnd=random.Random(300+b); i=rnd.randrange(0,len(ws)-2000)
        v.append(len(set(ws[i:i+2000]))/2000)
    ref.append((st.mean(v), fn[:-6]))
ref.sort()
print(f"  минимум по корпусам: {ref[0][0]:.3f} ({ref[0][1]}); медиана {st.median([x for x,_ in ref]):.3f}; максимум {ref[-1][0]:.3f} ({ref[-1][1]})")
print(f"  ниже «банного» (0.332): "+(", ".join(n for x,n in ref if x<0.332) or "ни одного из %d корпусов"%len(ref)))
