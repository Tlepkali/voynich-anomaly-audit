import json, collections, math, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
TOK={"A":[],"B":[]}
for r in [r for r in rows if r["locus"]=="P"]:
    L=pages.get(r["page"],{}).get("L","?")
    if L in TOK: TOK[L]+=[w for w in r["words"] if '?' not in w]
N=min(len(TOK["A"]),len(TOK["B"]))
def gl(w): return metrics.merge(w)
def mean(x): return sum(x)/len(x) if x else 0.0

print("="*84)
print("ТЕСТ 1. Куда ушло o: раскладка по местам в слове (равная глубина, 15 повторов)")
print("="*84)
acc={L:collections.defaultdict(list) for L in ("A","B")}
for k in range(15):
    r=random.Random(800+k)
    for L in ("A","B"):
        ty=list(collections.Counter(r.sample(TOK[L],N)))
        c=collections.defaultdict(collections.Counter)
        for w in ty:
            g=gl(w)
            if len(g)==1: c[g[0]]["одиночн"]+=1; continue
            c[g[0]]["начало"]+=1; c[g[-1]]["конец"]+=1
            for x in g[1:-1]: c[x]["внутри"]+=1
        for x in ("o","e","ee","a"):
            t=sum(c[x].values()) or 1
            for p in ("начало","внутри","конец"):
                acc[L][(x,p)].append(c[x][p]/t)
print(f"  {'знак':6s} {'место':10s} {'A':>8s} {'B':>8s} {'сдвиг':>8s}")
for x in ("o","e","ee","a"):
    for p in ("начало","внутри","конец"):
        a,b=mean(acc["A"][(x,p)]), mean(acc["B"][(x,p)])
        mark=" ←" if abs(b-a)>0.06 else ""
        print(f"  {x:6s} {p:10s} {a:8.1%} {b:8.1%} {b-a:+8.1%}{mark}")
    print()

print("="*84)
print("ТЕСТ 2. Минимальные пары: слова, различающиеся ровно одним знаком o↔e")
print("="*84)
cA=collections.Counter(TOK["A"]); cB=collections.Counter(TOK["B"])
scale=len(TOK["A"])/len(TOK["B"])
pairs=[]
allw=set(cA)|set(cB)
for w in allw:
    g=gl(w)
    for i,x in enumerate(g):
        if x!="o": continue
        v="".join(g[:i]+["e"]+g[i+1:])
        if v in allw and v>w:
            pairs.append((w,v))
seen=set(); uniq=[]
for w,v in pairs:
    if (w,v) in seen: continue
    seen.add((w,v)); uniq.append((w,v))
print(f"  найдено пар «слово с o» / «то же слово с e»: {len(uniq)}")
tot_oA=tot_eA=tot_oB=tot_eB=0
show=[]
for w,v in uniq:
    oA,eA,oB,eB = cA[w],cA[v],cB[w],cB[v]
    tot_oA+=oA; tot_eA+=eA; tot_oB+=oB; tot_eB+=eB
    if oA+eA+oB+eB>=40: show.append((oA+eA+oB+eB,w,v,oA,eA,oB,eB))
show.sort(reverse=True)
print(f"\n  {'пара':26s} {'A: o / e':>14s} {'B: o / e':>14s}   доля e: A → B")
for _,w,v,oA,eA,oB,eB in show[:10]:
    fa=eA/(oA+eA) if oA+eA else float('nan')
    fb=eB/(oB+eB) if oB+eB else float('nan')
    print(f"  {w+' / '+v:26s} {str(oA)+' / '+str(eA):>14s} {str(oB)+' / '+str(eB):>14s}   {fa:5.0%} → {fb:5.0%}")
print(f"\n  ИТОГО по всем парам: в A вариант с e составляет {tot_eA/(tot_oA+tot_eA):.1%} "
      f"({tot_eA}/{tot_oA+tot_eA})")
print(f"                        в B вариант с e составляет {tot_eB/(tot_oB+tot_eB):.1%} "
      f"({tot_eB}/{tot_oB+tot_eB})")
