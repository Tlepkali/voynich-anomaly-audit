import json, collections, math, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows=D["rows"]
VOY=[w for r in rows if r["locus"]=="P" for w in r["words"] if '?' not in w]
lat=open("ref/latin.clean").read().split()[:len(VOY)]
eng=open("ref/english.clean").read().split()[:len(VOY)]
def stats(words):
    ty=collections.Counter(words); T=len(words)
    H=-sum(n/T*math.log2(n/T) for n in ty.values())
    hap=sum(1 for v in ty.values() if v==1)/len(ty)
    return len(ty), len(ty)/T, hap, H
def randcut(words, seed):
    """тот же поток знаков, но разрезанный в случайных местах с тем же распределением длин"""
    rnd=random.Random(seed)
    stream="".join(words); lens=[len(w) for w in words]; rnd.shuffle(lens)
    out=[]; i=0
    for L in lens:
        if i>=len(stream): break
        out.append(stream[i:i+L]); i+=L
    return out
print("="*96)
print("НЕСУТ ЛИ ПРОБЕЛЫ ИНФОРМАЦИЮ: настоящая сегментация против случайной той же зернистости")
print("="*96)
print(f"  {'корпус':28s} {'типов':>7s} {'TTR':>7s} {'хапаксы':>8s} {'H(слово)':>9s}")
for lab, ws in (("РУКОПИСЬ ВОЙНИЧА",VOY),("латынь",lat),("английский",eng)):
    a=stats(ws)
    rs=[stats(randcut(ws,100+k)) for k in range(6)]
    m=lambda i: sum(r[i] for r in rs)/len(rs)
    print(f"  {lab:28s} {a[0]:7d} {a[1]:7.3f} {a[2]:8.3f} {a[3]:9.3f}   ← настоящая")
    print(f"  {'  случайные разрезы':28s} {m(0):7.0f} {m(1):7.3f} {m(2):8.3f} {m(3):9.3f}")
    print(f"  {'  выигрыш настоящей':28s} {(m(0)-a[0])/m(0):+7.1%} {'':7s} {'':8s} {m(3)-a[3]:+9.3f} бит\n")
print("="*96)
print("СЛИЯНИЕ СОСЕДНИХ ЕДИНИЦ: если настоящее слово длиннее, склейка должна помочь")
print("="*96)
def merge_pairs(ws,k=2): return ["".join(ws[i:i+k]) for i in range(0,len(ws)-k+1,k)]
def rep(w):
    ty=collections.Counter(w); T=len(w)
    same=sum(1 for a,b in zip(w,w[1:]) if a==b)
    exp=sum((n/T)**2 for n in ty.values())*(T-1)
    return (same/exp if exp else 0)
print(f"  {'вариант':28s} {'единиц':>7s} {'типов':>7s} {'TTR':>7s} {'хапаксы':>8s} {'повторы':>9s}")
for lab, ws in (("Войнич как есть",VOY),("Войнич, склейка по 2",merge_pairs(VOY)),
                ("Войнич, склейка по 3",merge_pairs(VOY,3)),
                ("латынь как есть",lat),("латынь, склейка по 2",merge_pairs(lat))):
    ty=collections.Counter(ws)
    print(f"  {lab:28s} {len(ws):7d} {len(ty):7d} {len(ty)/len(ws):7.3f} "
          f"{sum(1 for v in ty.values() if v==1)/len(ty):8.3f} {rep(ws):8.3f}×")
