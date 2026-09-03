import json, collections, math, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows, pages = D["rows"], D["pages"]
P=[r for r in rows if r["locus"]=="P"]
LINES=[]
for r in P:
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=3: LINES.append({"w":ws,"pos":r["pos"],"page":r["page"]})
ALL=[w for l in LINES for w in l["w"]]; VOC=collections.Counter(ALL)
FIRST=[l["w"][0] for l in LINES]; LAST=[l["w"][-1] for l in LINES]
MID=[w for l in LINES for w in l["w"][1:-1]]
def wilson(k,n):
    if n==0: return (0,0)
    p=k/n; z=1.96; d=1+z*z/n
    c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (c-h,c+h)

print("="*74)
print("ТЕСТ 1 (исправлен). Снимаем первый ЗНАК, а не букву")
print("="*74)
print(f"  {'знак':7s} {'позиция':13s} {'n':>5s} {'остаток — слово':>16s} {'95% интервал':>17s}")
G=collections.defaultdict(lambda: collections.defaultdict(list))
for name, ws in (("начало строки",FIRST),("середина",MID)):
    for w in ws:
        g=metrics.merge(w)
        if len(g)>2: G[g[0]][name].append("".join(g[1:]))
for g in sorted(G, key=lambda g: -sum(len(v) for v in G[g].values()))[:9]:
    rows_=[]
    for name in ("начало строки","середина"):
        sel=G[g].get(name,[])
        if len(sel)<30: continue
        k=sum(1 for r in sel if r in VOC); lo,hi=wilson(k,len(sel))
        rows_.append((name,len(sel),k/len(sel),lo,hi))
    if len(rows_)==2:
        a,b=rows_
        flag=" ←" if (a[3]>b[4] or b[3]>a[4]) else ""
        for name,n,p,lo,hi in rows_:
            print(f"  {g:7s} {name:13s} {n:5d} {p:15.1%}  [{lo:5.1%},{hi:5.1%}]{flag if name=='начало строки' else ''}")
        print()

print("="*74)
print("ТЕСТ 3 (исправлен). Словарь краёв — с честным контролем той же выборки")
print("="*74)
rnd=random.Random(11)
def unique_share(sample, pool):
    """доля типов выборки, не встречающихся в остальном тексте"""
    rest=collections.Counter(pool)
    for w in sample: rest[w]-=1
    rest={w for w,n in rest.items() if n>0}
    ts=set(sample); return len(ts-rest)/len(ts), len(ts)
sh_f,n_f = unique_share(FIRST, ALL)
sh_l,n_l = unique_share(LAST, ALL)
ctrl=rnd.sample(MID, len(FIRST))
sh_c,n_c = unique_share(ctrl, ALL)
print(f"  начало строки: типов {n_f:5d}, встречаются ТОЛЬКО там {sh_f:.1%}")
print(f"  конец строки:  типов {n_l:5d}, только там {sh_l:.1%}")
print(f"  контроль (столько же слов из середины): типов {n_c:5d}, только там {sh_c:.1%}")
print(f"  → превышение над контролем: начало ×{sh_f/sh_c:.2f}, конец ×{sh_l/sh_c:.2f}")

print("\n"+"="*74)
print("ПРОФИЛЬ ПО ОТНОСИТЕЛЬНОМУ МЕСТУ В СТРОКЕ (десять корзин)")
print("="*74)
bins=[[] for _ in range(10)]
for l in LINES:
    n=len(l["w"])
    for i,w in enumerate(l["w"]):
        bins[min(9,int(10*i/n))].append(w)
print(f"  {'корзина':9s} {'n':>6s} {'ср.длина':>9s} {'m в конце':>10s} {'нач. y/d/s':>11s} {'нач. c/o':>9s}")
for i,b in enumerate(bins):
    mu=sum(len(w) for w in b)/len(b)
    m=sum(1 for w in b if w.endswith('m'))/len(b)
    yds=sum(1 for w in b if w[0] in 'yds')/len(b)
    co=sum(1 for w in b if w[0] in 'co')/len(b)
    bar='█'*int(mu*3-13)
    print(f"  {i*10:3d}–{i*10+10:3d}% {len(b):6d} {mu:9.2f} {m:10.1%} {yds:11.1%} {co:9.1%}  {bar}")
