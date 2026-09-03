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

def slots(types):
    posc=collections.defaultdict(collections.Counter)
    for w in types:
        g=gl(w)
        if len(g)==1: posc[g[0]]["одиночн"]+=1; continue
        posc[g[0]]["начало"]+=1; posc[g[-1]]["конец"]+=1
        for x in g[1:-1]: posc[x]["внутри"]+=1
    return posc
def inventory(types, place):
    posc=slots(types); c=collections.Counter()
    for g,d in posc.items(): c[g]=d[place]
    T=sum(c.values()) or 1
    return [(g, n/T) for g,n in c.most_common(8)]

print("СЛОТОВЫЙ НАБОР ПО ЯЗЫКАМ (на уникальных словах, равная глубина выборки)")
print("="*92)
r=random.Random(11)
TY={L: list(collections.Counter(r.sample(TOK[L],N))) for L in ("A","B")}
for place in ("начало","внутри","конец"):
    print(f"\n  {place.upper()}")
    for L in ("A","B"):
        inv=inventory(TY[L], place)
        print(f"     {L}: " + "  ".join(f"{g} {p:.0%}" for g,p in inv))

print("\n"+"="*92)
print("ЧИСТОТА СЛОТА: какая доля вхождений знака приходится на его главное место")
print("="*92)
acc={L:collections.defaultdict(list) for L in ("A","B")}
for k in range(15):
    rr=random.Random(700+k)
    ty={L: list(collections.Counter(rr.sample(TOK[L],N))) for L in ("A","B")}
    for L in ("A","B"):
        posc=slots(ty[L])
        for g,d in posc.items():
            tot=sum(d.values())
            if tot<40: continue
            acc[L][g].append(max(d[p] for p in ("начало","внутри","конец"))/tot)
common=sorted(set(acc["A"])&set(acc["B"]), key=lambda g:-mean(acc["B"][g]))
print(f"  {'знак':8s} {'A':>8s} {'B':>8s} {'разница':>9s}")
big=[]
for g in common:
    a,b=mean(acc["A"][g]), mean(acc["B"][g])
    big.append((b-a,g,a,b))
big.sort(reverse=True)
for d,g,a,b in big[:6]+[("—",)*4]+big[-5:]:
    if d=="—": print("  " + "·"*34); continue
    print(f"  {g:8s} {a:8.0%} {b:8.0%} {d:+9.1%}")
print(f"\n  в среднем по всем знакам: A {mean([x[2] for x in big]):.1%}   B {mean([x[3] for x in big]):.1%}")

print("\n"+"="*92)
print("СИЛА КОНКУРЕНЦИИ ЗА МЕСТО: избегают ли знаки одного слота друг друга сильнее в B")
print("="*92)
def gap(types, seed):
    sets=[set(gl(w)) for w in types]; M=len(sets)
    cnt=collections.Counter()
    for s in sets:
        for g in s: cnt[g]+=1
    com=[g for g,n in cnt.items() if n/M>=0.02]
    posc=slots(types)
    sl={}
    for g in com:
        d=posc[g]; sl[g]=max(("начало","внутри","конец"), key=lambda k:d[k])
    def lr(a,b):
        n=sum(1 for s in sets if a in s and b in s); e=cnt[a]*cnt[b]/M
        return (math.log2((n+.5)/(e+.5)), e)
    same=[]; diff=[]
    for i,a in enumerate(com):
        for b in com[i+1:]:
            v,e=lr(a,b)
            if e<25: continue
            (same if sl[a]==sl[b] else diff).append(v)
    if not same or not diff: return None
    obs=mean(diff)-mean(same)
    rnd=random.Random(seed); labs=[sl[g] for g in com]; nulls=[]
    for _ in range(120):
        rnd.shuffle(labs); sl2={g:labs[i] for i,g in enumerate(com)}
        s2=[];d2=[]
        for i,a in enumerate(com):
            for b in com[i+1:]:
                v,e=lr(a,b)
                if e<25: continue
                (s2 if sl2[a]==sl2[b] else d2).append(v)
        if s2 and d2: nulls.append(mean(d2)-mean(s2))
    nulls.sort()
    return obs, mean(same), mean(diff), nulls[int(.975*len(nulls))]
for L in ("A","B"):
    res=gap(TY[L], 30+ord(L))
    if res:
        obs,s,d,n95=res
        print(f"  язык {L}: одно место {s:+.2f}   разные места {d:+.2f}   разрыв {obs:+.2f}   "
              f"случайный потолок {n95:+.2f}  {'значимо ✓' if obs>n95 else 'не значимо ·'}")
