import json, collections, hashlib, math, sys, random
sys.path.insert(0,".")
N=4000
lat=open("ref/latin.clean").read().split()
D=json.load(open("parsed.json")); rows=D["rows"]
VOY=[w for r in rows if r["locus"]=="P" for w in r["words"] if '?' not in w][:N]
AL="abcdefghijklmnopqrstuvwxy"          # 25 знаков, как у EVA
def h_fixed(w, k=5):
    d=hashlib.sha256(w.encode()).digest()
    return "".join(AL[b % len(AL)] for b in d[:k])
def h_varlen(w):
    d=hashlib.sha256(w.encode()).digest()
    k=2+d[0]%7                          # длина 2..8, как в рукописи
    return "".join(AL[b % len(AL)] for b in d[1:1+k])
def h_len_preserve(w):                  # длина сохраняется от исходного слова
    d=hashlib.sha256(w.encode()).digest()
    return "".join(AL[d[i % len(d)] % len(AL)] for i in range(len(w)))
def rep(w):
    ty=collections.Counter(w); T=len(w)
    same=sum(1 for a,b in zip(w,w[1:]) if a==b)
    exp=sum((n/T)**2 for n in ty.values())*(T-1)
    return (same/exp if exp else 0)
def ed1(a,b):
    if a==b or abs(len(a)-len(b))>1: return False
    if len(a)==len(b): return sum(x!=y for x,y in zip(a,b))==1
    s,l=(a,b) if len(a)<len(b) else (b,a)
    return any(l[:i]+l[i+1:]==s for i in range(len(l)))
def mi_pos(ws):
    j=collections.Counter()
    for w in ws:
        for i,c in enumerate(w):
            p="1" if len(w)==1 else ("b" if i==0 else ("e" if i==len(w)-1 else "m"))
            j[(c,p)]+=1
    T=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (a,b),n in j.items(): pg[a]+=n; pp[b]+=n
    return sum(n/T*math.log2((n/T)/((pg[a]/T)*(pp[b]/T))) for (a,b),n in j.items())
def zipf(ws):
    f=sorted(collections.Counter(ws).values(), reverse=True)[:400]
    xs=[math.log(i+1) for i in range(len(f))]; ys=[math.log(v) for v in f]
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    return sum((a-mx)*(b-my) for a,b in zip(xs,ys))/sum((a-mx)**2 for a in xs)
def show(ws, lab):
    w=ws[:N]; ty=collections.Counter(w)
    ln=[len(x) for x in w]; mu=sum(ln)/len(ln)
    sd=(sum((x-mu)**2 for x in ln)/len(ln))**0.5
    e1=sum(1 for a,b in zip(w,w[1:]) if ed1(a,b))/(len(w)-1)
    hap=sum(1 for v in ty.values() if v==1)/len(ty)
    print(f"  {lab:34s} {len(ty):5d} {len(ty)/len(w):7.3f} {hap:7.3f} {zipf(w):7.2f} "
          f"{mu:6.2f} {sd/mu:6.3f} {mi_pos(w):8.3f} {rep(w):7.3f}× {e1:7.3f}")
print("="*112)
print("ГИПОТЕЗА ХЭША: прогоняем латынь через хэш-функцию")
print("="*112)
print(f"  {'корпус':34s} {'типов':>5s} {'TTR':>7s} {'хапакс':>7s} {'Ципф':>7s} {'ср.дл':>6s} "
      f"{'CV дл':>6s} {'слотов.':>8s} {'повторы':>8s} {'отл.1':>7s}")
show(VOY,"РУКОПИСЬ ВОЙНИЧА")
print("  "+"-"*108)
show(lat,"латынь без изменений")
show([h_fixed(w) for w in lat],"хэш, фиксированная длина 5")
show([h_varlen(w) for w in lat],"хэш, длина 2–8 от хэша")
show([h_len_preserve(w) for w in lat],"хэш, длина от исходного слова")
