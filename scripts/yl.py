import json, collections, math, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
TOK={"A":[],"B":[]}
for r in [r for r in rows if r["locus"]=="P"]:
    L=pages.get(r["page"],{}).get("L","?")
    if L in TOK: TOK[L]+=[w for w in r["words"] if '?' not in w]
cA=collections.Counter(TOK["A"]); cB=collections.Counter(TOK["B"]); V=set(cA)|set(cB)
def gl(w): return metrics.merge(w)
def lo(p): return math.log((p+.02)/(1-p+.02))
# все минимальные пары y/l с записью левого и правого соседа и места в слове
recs=[]; seen=set()
for w in V:
    g=gl(w)
    for i,x in enumerate(g):
        if x!="y": continue
        ng=g[:i]+["l"]+g[i+1:]; v="".join(ng)
        if v not in V or gl(v)!=ng: continue
        if (w,v) in seen: continue
        seen.add((w,v))
        left = g[i-1] if i>0 else "^"
        right= g[i+1] if i+1<len(g) else "$"
        place= "начало" if i==0 else ("конец" if i==len(g)-1 else "внутри")
        recs.append((w,v,left,right,place))
print(f"минимальных пар y/l: {len(recs)}\n")
def table(keyf, title, minn=25):
    print("="*84); print(title); print("="*84)
    by=collections.defaultdict(list)
    for r in recs: by[keyf(r)].append(r)
    out=[]
    for k,lst in by.items():
        yA=sum(cA[a] for a,b,_,_,_ in lst); lA=sum(cA[b] for a,b,_,_,_ in lst)
        yB=sum(cB[a] for a,b,_,_,_ in lst); lB=sum(cB[b] for a,b,_,_,_ in lst)
        if min(yA+lA, yB+lB)<minn: continue
        fa=lA/(yA+lA); fb=lB/(yB+lB)
        rnd=random.Random(4); r_=[]
        for _ in range(1500):
            s=[lst[rnd.randrange(len(lst))] for _ in range(len(lst))]
            a1=sum(cA[a] for a,b,_,_,_ in s); a2=sum(cA[b] for a,b,_,_,_ in s)
            b1=sum(cB[a] for a,b,_,_,_ in s); b2=sum(cB[b] for a,b,_,_,_ in s)
            if a1+a2 and b1+b2: r_.append(lo(b2/(b1+b2))-lo(a2/(a1+a2)))
        r_.sort()
        out.append((lo(fb)-lo(fa), k, len(lst), yA+lA, yB+lB, fa, fb,
                    r_[int(.025*len(r_))], r_[int(.975*len(r_))]))
    out.sort(reverse=True)
    print(f"  {'контекст':12s} {'пар':>4s} {'слов A':>7s} {'слов B':>7s} {'доля l: A':>10s} {'B':>7s} {'сдвиг':>7s} {'интервал':>17s}")
    for sh,k,n,tA,tB,fa,fb,L,H in out:
        sig="✓" if (L>0 or H<0) else "·"
        print(f"  {str(k):12s} {n:4d} {tA:7d} {tB:7d} {fa:10.0%} {fb:7.0%} {sh:+7.2f} [{L:+5.2f},{H:+5.2f}] {sig}")
    print()
table(lambda r: r[3], "ПО ПРАВОМУ СОСЕДУ")
table(lambda r: r[2], "ПО ЛЕВОМУ СОСЕДУ")
table(lambda r: r[4], "ПО МЕСТУ В СЛОВЕ")
