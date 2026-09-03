import json, collections, math, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
TOK={"A":[],"B":[]}
for r in [r for r in rows if r["locus"]=="P"]:
    L=pages.get(r["page"],{}).get("L","?")
    if L in TOK: TOK[L]+=[w for w in r["words"] if '?' not in w]
cA=collections.Counter(TOK["A"]); cB=collections.Counter(TOK["B"]); V=set(cA)|set(cB)
def gl(w): return metrics.merge(w)
gc=collections.Counter()
for w in TOK["A"]+TOK["B"]:
    for g in gl(w): gc[g]+=1
T=sum(gc.values()); GS={g for g,n in gc.items() if n/T>=0.004}
# минимальные пары с записью окружения
P=collections.defaultdict(lambda: collections.defaultdict(list))
seen=set()
for w in V:
    g=gl(w)
    for i,x in enumerate(g):
        if x not in GS: continue
        for y in GS:
            if y==x: continue
            ng=g[:i]+[y]+g[i+1:]; v="".join(ng)
            if v not in V or gl(v)!=ng: continue
            key=tuple(sorted((x,y))); a,b=(w,v) if key[0]==x else (v,w)
            if (key,a,b) in seen: continue
            seen.add((key,a,b))
            right = g[i+1] if i+1<len(g) else "$"
            P[key][right].append((a,b))
def lo(p): return math.log((p+.02)/(1-p+.02))
res=[]
for key,byctx in P.items():
    X,Y=key
    buckets=[]
    for ctx,lst in byctx.items():
        oA=sum(cA[a] for a,b in lst); eA=sum(cA[b] for a,b in lst)
        oB=sum(cB[a] for a,b in lst); eB=sum(cB[b] for a,b in lst)
        if min(oA+eA,oB+eB)<60: continue
        buckets.append((ctx,len(lst),oA,eA,oB,eB, lo(eB/(oB+eB))-lo(eA/(oA+eA))))
    if len(buckets)<3: continue
    sh=[b[6] for b in buckets]
    spread=max(sh)-min(sh)
    # перестановочный тест: перемешиваем принадлежность слов к контекстам
    allp=[(a,b) for lst in byctx.values() for a,b in lst]
    sizes=[len(byctx[c]) for c,_,_,_,_,_,_ in buckets]
    rnd=random.Random(9); nulls=[]
    for _ in range(300):
        rnd.shuffle(allp); k=0; sh2=[]
        for s in sizes:
            chunk=allp[k:k+s]; k+=s
            oA=sum(cA[a] for a,b in chunk); eA=sum(cA[b] for a,b in chunk)
            oB=sum(cB[a] for a,b in chunk); eB=sum(cB[b] for a,b in chunk)
            if min(oA+eA,oB+eB)>=20: sh2.append(lo(eB/(oB+eB))-lo(eA/(oA+eA)))
        if len(sh2)>=3: nulls.append(max(sh2)-min(sh2))
    if len(nulls)<100: continue
    nulls.sort(); n95=nulls[int(.95*len(nulls))]
    res.append((spread-n95, X,Y, buckets, spread, n95))
res.sort(reverse=True)
print("="*100)
print("ЗАМЕНЫ, СИЛА КОТОРЫХ ЗАВИСИТ ОТ ОКРУЖЕНИЯ  (сдвиг доли второго варианта, log-odds)")
print("="*100)
print("разброс = разница между самым сильным и самым слабым контекстом; порог — перестановочный\n")
shown=0
for excess,X,Y,buckets,spread,n95 in res:
    if excess<=0: continue
    shown+=1
    if shown>6: break
    print(f"  {X} → {Y}:  разброс по контекстам {spread:+.2f} при случайном пороге {n95:.2f}")
    for ctx,n,oA,eA,oB,eB,s in sorted(buckets,key=lambda b:-b[6]):
        fa=eA/(oA+eA); fb=eB/(oB+eB)
        print(f"      перед «{ctx:4s}»  пар {n:3d}   доля {Y} : A {fa:5.0%} → B {fb:5.0%}   сдвиг {s:+6.2f}")
    print()
print(f"  замен с контекстной зависимостью выше случайного порога: "
      f"{sum(1 for r in res if r[0]>0)} из {len(res)} проверенных")
