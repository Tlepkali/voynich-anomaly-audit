import json, collections, sys
sys.path.insert(0,".")
D=json.load(open("parsed.json")); rows=D["rows"]; pages=D["pages"]
SEC={"T":"текст","H":"травник","A":"астрон","Z":"зодиак","B":"«банный»","C":"космол","P":"аптечн","S":"рецепты"}
P=[r for r in rows if r["locus"]=="P"]
LINES=[]
for r in P:
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=3:
        m=pages.get(r["page"],{})
        LINES.append({"w":ws,"page":r["page"],"I":m.get("I","?"),"L":m.get("L","?"),"H":m.get("H","?")})
ALL=[w for l in LINES for w in l["w"]]
print("="*92); print("ОТКУДА БЕРУТСЯ ПОВТОРЫ ПОДРЯД"); print("="*92)
pairs=[(l,i) for l in LINES for i in range(len(l["w"])-1) if l["w"][i]==l["w"][i+1]]
print(f"  всего повторов подряд: {len(pairs)} на {sum(len(l['w'])-1 for l in LINES)} пар\n")
print("  какие слова повторяются:")
c=collections.Counter(l["w"][i] for l,i in pairs)
tot=collections.Counter(ALL)
for w,n in c.most_common(12):
    print(f"     {w:10s} повторов {n:3d}   всего вхождений {tot[w]:4d}   доля {n/tot[w]:5.1%}")
print(f"\n  различных слов, участвующих в повторах: {len(c)} из {len(tot)} в словаре")
print("\n  по разделам (доля пар, являющихся повтором):")
by=collections.defaultdict(lambda:[0,0])
for l in LINES:
    k=SEC.get(l["I"],l["I"]); by[k][1]+=len(l["w"])-1
    by[k][0]+=sum(1 for i in range(len(l["w"])-1) if l["w"][i]==l["w"][i+1])
for k,(a,b) in sorted(by.items(), key=lambda kv:-kv[1][0]/max(1,kv[1][1])):
    if b<300: continue
    print(f"     {k:10s} {a:4d}/{b:6d} = {a/b:6.2%}")
print("\n  по языку Карриера:")
byl=collections.defaultdict(lambda:[0,0])
for l in LINES:
    byl[l["L"]][1]+=len(l["w"])-1
    byl[l["L"]][0]+=sum(1 for i in range(len(l["w"])-1) if l["w"][i]==l["w"][i+1])
for k,(a,b) in byl.items():
    if b>300: print(f"     язык {k}: {a:4d}/{b:6d} = {a/b:6.2%}")
print("\n  место в строке:")
pos=collections.defaultdict(lambda:[0,0])
for l in LINES:
    n=len(l["w"])
    for i in range(n-1):
        k=min(4,int(5*i/max(1,n-1)))
        pos[k][1]+=1; pos[k][0]+= (l["w"][i]==l["w"][i+1])
for k in sorted(pos):
    a,b=pos[k]
    print(f"     {k*20:3d}–{k*20+20:3d}% строки  {a:4d}/{b:5d} = {a/b:6.2%}")
print("\n  сосредоточены ли повторы на немногих страницах:")
byp=collections.defaultdict(lambda:[0,0])
for l in LINES:
    byp[l["page"]][1]+=len(l["w"])-1
    byp[l["page"]][0]+=sum(1 for i in range(len(l["w"])-1) if l["w"][i]==l["w"][i+1])
pgs=[(a/b,a,b,p) for p,(a,b) in byp.items() if b>=100]
pgs.sort(reverse=True)
print(f"     страниц с ≥100 парами: {len(pgs)}, из них без единого повтора: {sum(1 for r in pgs if r[1]==0)}")
for r,a,b,p in pgs[:6]:
    print(f"     {p:8s} {a:3d}/{b:4d} = {r:6.2%}  раздел {SEC.get(pages.get(p,{}).get('I','?'),'?')}")
print("\n  серии из трёх и более одинаковых подряд:")
runs=collections.Counter()
for l in LINES:
    w=l["w"]; i=0
    while i<len(w):
        j=i
        while j+1<len(w) and w[j+1]==w[i]: j+=1
        if j-i+1>=3: runs[(w[i], j-i+1)]+=1
        i=j+1
for (w,n),k in runs.most_common(10): print(f"     {w} × {n} подряд — {k} раз")
