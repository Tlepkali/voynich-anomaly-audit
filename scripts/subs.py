import json, collections, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
TOK={"A":[],"B":[]}
for r in [r for r in rows if r["locus"]=="P"]:
    L=pages.get(r["page"],{}).get("L","?")
    if L in TOK: TOK[L]+=[w for w in r["words"] if '?' not in w]
cA=collections.Counter(TOK["A"]); cB=collections.Counter(TOK["B"]); V=set(cA)|set(cB)
def gl(w): return metrics.merge(w)
GS=set(g for w in V for g in gl(w))
GS={g for g in GS if sum(1 for w in V if g in gl(w))>=30}
print(f"словарь {len(V)}, знаков в рассмотрении {len(GS)}")

# собираем минимальные пары: замена одного знака и удаление одного знака
pairs=collections.defaultdict(list)   # (X,Y) -> список (слово_с_X, слово_с_Y)
seen=set()
for w in V:
    g=gl(w)
    for i,x in enumerate(g):
        if x not in GS: continue
        for y in GS|{"∅"}:
            if y==x: continue
            ng = g[:i]+g[i+1:] if y=="∅" else g[:i]+[y]+g[i+1:]
            if not ng: continue
            v="".join(ng)
            if v not in V or gl(v)!=ng: continue      # склейка не должна перестроить слово
            key=(x,y) if y=="∅" else tuple(sorted((x,y)))
            a,b=(w,v) if (y=="∅" or key[0]==x) else (v,w)
            if (key,a,b) in seen: continue
            seen.add((key,a,b)); pairs[key].append((a,b))

rows_=[]
for key,lst in pairs.items():
    X,Y=key
    oA=sum(cA[a] for a,b in lst); eA=sum(cA[b] for a,b in lst)
    oB=sum(cB[a] for a,b in lst); eB=sum(cB[b] for a,b in lst)
    tA,tB=oA+eA,oB+eB
    if tA<80 or tB<80: continue
    fa,fb=eA/tA, eB/tB
    rnd=random.Random(3); r=[]
    for _ in range(2000):
        s=[lst[rnd.randrange(len(lst))] for _ in range(len(lst))]
        na=sum(cA[a] for a,b in s); ea=sum(cA[b] for a,b in s)
        nb=sum(cB[a] for a,b in s); eb=sum(cB[b] for a,b in s)
        if na+ea and nb+eb: r.append(eb/(nb+eb)-ea/(na+ea))
    r.sort()
    lo,hi=(r[int(.025*len(r))], r[int(.975*len(r))]) if r else (0,0)
    rows_.append((abs(fb-fa), X,Y, len(lst), tA,tB, fa,fb, lo,hi))
rows_.sort(reverse=True)
print("\n" + "="*104)
print("ЛОКАЛЬНЫЕ ЗАМЕНЫ МЕЖДУ A И B  (доля второго варианта; ∅ = знак отсутствует)")
print("="*104)
print(f"  {'замена':14s} {'пар':>5s} {'слов A':>7s} {'слов B':>7s} {'доля в A':>9s} {'доля в B':>9s} {'сдвиг':>8s} {'95% интервал':>20s}")
shown=0
for d,X,Y,n,tA,tB,fa,fb,lo,hi in rows_:
    sig = (lo>0 or hi<0)
    if not sig or d<0.10: continue
    shown+=1
    print(f"  {X+' → '+Y:14s} {n:5d} {tA:7d} {tB:7d} {fa:9.1%} {fb:9.1%} {fb-fa:+8.1%} "
          f"[{lo:+6.1%},{hi:+6.1%}]")
print(f"\n  значимых сдвигов ≥10 пунктов: {shown} из {len(rows_)} проверенных замен")
print("  (порог по объёму: не менее 80 словоупотреблений в каждом языке)")
