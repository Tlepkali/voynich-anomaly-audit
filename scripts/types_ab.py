import json, collections, math, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
TOK={"A":[], "B":[]}
for r in [r for r in rows if r["locus"]=="P"]:
    L=pages.get(r["page"],{}).get("L","?")
    if L in TOK: TOK[L]+= [w for w in r["words"] if '?' not in w]
print(f"токенов: A {len(TOK['A'])}, B {len(TOK['B'])}")
N=min(len(TOK["A"]), len(TOK["B"]))
def gl(w): return metrics.merge(w)
def mean(x): return sum(x)/len(x) if x else 0.0
def posclass(n,i): return "1" if n==1 else ("b" if i==0 else ("e" if i==n-1 else "m"))
def mi(types):
    j=collections.Counter()
    for w in types:
        g=gl(w)
        for i,c in enumerate(g): j[(c,posclass(len(g),i))]+=1
    T=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (a,b),n in j.items(): pg[a]+=n; pp[b]+=n
    return sum(n/T*math.log2((n/T)/((pg[a]/T)*(pp[b]/T))) for (a,b),n in j.items())
def hcond(types):
    """условная энтропия следующего знака внутри слова (по типам, каждое слово 1 раз)"""
    u=[]
    for w in types: u.extend(["^"]+gl(w)+["$"])
    c=collections.Counter(u); T=len(u)
    h1=-sum(n/T*math.log2(n/T) for n in c.values())
    b=collections.Counter(zip(u,u[1:])); M=sum(b.values())
    return -sum(n/M*math.log2(n/M) for n in b.values())-h1

print("\n"+"="*84)
print("ПАНЕЛЬ ПО ТИПАМ, при равном числе просмотренных токенов (20 повторов)")
print("="*84)
acc=collections.defaultdict(lambda: collections.defaultdict(list))
for k in range(20):
    for L in ("A","B"):
        r=random.Random(300+k); sub=r.sample(TOK[L], N)
        ty=list(collections.Counter(sub))
        a=acc[L]
        a["n"].append(len(ty))
        ln=[len(gl(w)) for w in ty]; mu=mean(ln)
        a["len"].append(mu); a["cv"].append((mean([(x-mu)**2 for x in ln])**0.5)/mu)
        a["mi"].append(mi(ty)); a["h"].append(hcond(ty))
        a["gly"].append(len({g for w in ty for g in gl(w)}))
print(f"  {'мера':38s} {'язык A':>12s} {'язык B':>12s}")
LAB=[("n","уникальных слов на равный объём"),("len","средняя длина, знаков"),
     ("cv","разброс длин (CV)"),("gly","размер набора знаков"),
     ("mi","жёсткость позиций I(знак;место)"),("h","предсказуемость следующего знака h2")]
for k,lab in LAB:
    print(f"  {lab:38s} {mean(acc['A'][k]):12.3f} {mean(acc['B'][k]):12.3f}")

print("\n"+"="*84)
print("ПЕРЕСЕЧЕНИЕ СЛОВАРЕЙ")
print("="*84)
sa=set(TOK["A"]); sb=set(TOK["B"])
inter=sa&sb
print(f"  типов в A {len(sa)}, в B {len(sb)}, общих {len(inter)}")
print(f"  доля словаря A, встречающаяся в B: {len(inter)/len(sa):.1%}")
print(f"  доля словаря B, встречающаяся в A: {len(inter)/len(sb):.1%}")
print(f"  Жаккар: {len(inter)/len(sa|sb):.3f}")
ca=collections.Counter(TOK["A"]); cb=collections.Counter(TOK["B"])
for n in (50,200,1000):
    ta={w for w,_ in ca.most_common(n)}; tb={w for w,_ in cb.most_common(n)}
    print(f"  среди {n:4d} самых частых слов общих: {len(ta&tb):4d} ({len(ta&tb)/n:.0%})")

print("\n"+"="*84)
print("ЗНАКИ: доля СЛОВ (типов), содержащих знак")
print("="*84)
def share(types):
    c=collections.Counter()
    for w in types:
        for g in set(gl(w)): c[g]+=1
    return {g: v/len(types) for g,v in c.items()}
r=random.Random(1)
tya=list(collections.Counter(r.sample(TOK["A"],N))); tyb=list(collections.Counter(r.sample(TOK["B"],N)))
A=share(tya); B=share(tyb)
keys=sorted(set(A)|set(B), key=lambda g:-(A.get(g,0)+B.get(g,0)))
print(f"  {'знак':8s} {'A':>8s} {'B':>8s} {'B/A':>8s}")
for g in keys:
    if max(A.get(g,0),B.get(g,0))<0.03: continue
    ratio=(B.get(g,0)+1e-9)/(A.get(g,0)+1e-9)
    flag=" ←" if (ratio>1.6 or ratio<0.62) else ""
    print(f"  {g:8s} {A.get(g,0):8.1%} {B.get(g,0):8.1%} {ratio:8.2f}{flag}")
