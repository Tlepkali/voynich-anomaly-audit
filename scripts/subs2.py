import json, collections, math, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
TOK={"A":[],"B":[]}
for r in [r for r in rows if r["locus"]=="P"]:
    L=pages.get(r["page"],{}).get("L","?")
    if L in TOK: TOK[L]+=[w for w in r["words"] if '?' not in w]
cA=collections.Counter(TOK["A"]); cB=collections.Counter(TOK["B"]); V=set(cA)|set(cB)
def gl(w): return metrics.merge(w)
# базовые частоты знаков (на все знаки текста)
def gfreq(toks):
    c=collections.Counter()
    for w in toks:
        for g in gl(w): c[g]+=1
    T=sum(c.values()); return {g:n/T for g,n in c.items()}, T
fA,_=gfreq(TOK["A"]); fB,_=gfreq(TOK["B"])
GS={g for g in set(fA)|set(fB) if fA.get(g,0)>=0.002 and fB.get(g,0)>=0.002}
pairs=collections.defaultdict(list); seen=set()
for w in V:
    g=gl(w)
    for i,x in enumerate(g):
        if x not in GS: continue
        for y in GS:
            if y==x: continue
            ng=g[:i]+[y]+g[i+1:]; v="".join(ng)
            if v not in V or gl(v)!=ng: continue
            key=tuple(sorted((x,y)))
            a,b=(w,v) if key[0]==x else (v,w)
            if (key,a,b) in seen: continue
            seen.add((key,a,b)); pairs[key].append((a,b))
def lo(p): return math.log((p+1e-9)/(1-p+1e-9))
out=[]
for (X,Y),lst in pairs.items():
    oA=sum(cA[a] for a,b in lst); eA=sum(cA[b] for a,b in lst)
    oB=sum(cB[a] for a,b in lst); eB=sum(cB[b] for a,b in lst)
    if min(oA+eA,oB+eB)<150 or len(lst)<15: continue
    obs = lo(eB/(oB+eB)) - lo(eA/(oA+eA))
    # ожидание от одних базовых частот знаков
    exp = math.log(fB[Y]/fA[Y]) - math.log(fB[X]/fA[X])
    resid = obs-exp
    # согласованность: доля отдельных пар, сдвинувшихся в ту же сторону
    same=0; usable=0
    for a,b in lst:
        ta,tb=cA[a]+cA[b], cB[a]+cB[b]
        if ta<5 or tb<5: continue
        usable+=1
        if (cB[b]/tb - cA[b]/ta)*resid>0: same+=1
    cons=same/usable if usable else 0
    rnd=random.Random(7); r=[]
    for _ in range(1500):
        s=[lst[rnd.randrange(len(lst))] for _ in range(len(lst))]
        na=sum(cA[a] for a,b in s); ea=sum(cA[b] for a,b in s)
        nb=sum(cB[a] for a,b in s); eb=sum(cB[b] for a,b in s)
        if na+ea>0 and nb+eb>0 and ea>0 and eb>0 and na>0 and nb>0:
            r.append(lo(eb/(nb+eb))-lo(ea/(na+ea))-exp)
    r.sort()
    if len(r)<500: continue
    L,H=r[int(.025*len(r))], r[int(.975*len(r))]
    out.append((abs(resid), X,Y,len(lst),usable,cons,obs,exp,resid,L,H))
out.sort(reverse=True)
print("="*106)
print("ЛОКАЛЬНЫЕ ЗАМЕНЫ С ПОПРАВКОЙ НА БАЗОВЫЕ ЧАСТОТЫ ЗНАКОВ")
print("="*106)
print("остаток = наблюдаемый сдвиг минус тот, что объясняется общим изменением частоты обоих знаков")
print(f"\n  {'замена':12s} {'пар':>4s} {'набл.':>7s} {'ожид.':>7s} {'ОСТАТОК':>9s} {'95% интервал':>18s} {'согласов.':>10s}")
n=0
for d,X,Y,np_,us,cons,obs,exp,res,L,H in out:
    if not (L>0 or H<0) or abs(res)<0.7: continue
    n+=1
    print(f"  {X+' → '+Y:12s} {np_:4d} {obs:+7.2f} {exp:+7.2f} {res:+9.2f} [{L:+6.2f},{H:+6.2f}] {cons:9.0%} ({us})")
print(f"\n  значимых остатков |>0,7|: {n} из {len(out)} проверенных замен")
