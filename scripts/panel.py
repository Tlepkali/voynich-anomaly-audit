import json, collections, math, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
SEC={"H":"травник","P":"аптечный","B":"«банный»","T":"текст","C":"космол.","S":"рецепты"}
LINES=[]
for r in [r for r in rows if r["locus"]=="P"]:
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=3:
        m=pages.get(r["page"],{})
        LINES.append({"w":ws,"page":r["page"],"L":m.get("L","?"),"I":m.get("I","?"),"H":m.get("H","?")})
ALLW=[w for l in LINES for w in l["w"]]
def gl(w): return metrics.merge(w)
def mean(x): return sum(x)/len(x) if x else 0.0
def lcp(a,b):
    ga,gb=gl(a),gl(b); n=0
    for x,y in zip(ga,gb):
        if x!=y: break
        n+=1
    return n
def posclass(n,i): return "1" if n==1 else ("b" if i==0 else ("e" if i==n-1 else "m"))
def mi(words):
    j=collections.Counter()
    for w in words:
        g=gl(w)
        for i,c in enumerate(g): j[(c,posclass(len(g),i))]+=1
    T=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (a,b),n in j.items(): pg[a]+=n; pp[b]+=n
    return sum(n/T*math.log2((n/T)/((pg[a]/T)*(pp[b]/T))) for (a,b),n in j.items())
def h12(words):
    u=[]
    for w in words: u.extend(gl(w)); u.append(" ")
    c=collections.Counter(u); T=len(u)
    h1=-sum(n/T*math.log2(n/T) for n in c.values())
    b=collections.Counter(zip(u,u[1:])); M=sum(b.values())
    return h1, -sum(n/M*math.log2(n/M) for n in b.values())-h1
def zipf(freqs):
    f=sorted(freqs,reverse=True)[:400]
    xs=[math.log(i+1) for i in range(len(f))]; ys=[math.log(v) for v in f]
    n=len(xs); mx=mean(xs); my=mean(ys)
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)

CELLS=[("2","B"),("3","S"),("1","H"),("2","H"),("2","T"),("1","P"),("5","H")]
rnd=random.Random(1)
print("="*104)
print("ПАНЕЛЬ A — меры, слабо зависящие от объёма (все ячейки)")
print("="*104)
print(f"  {'ячейка':22s} {'яз':4s} {'слов':>6s} {'ср.дл':>6s} {'CV':>5s} {'строка':>7s} {'копир.':>7s} "
      f"{'повт.×':>7s} {'отл.1':>6s} {'нач.стр':>8s}")
store={}
for h,s in CELLS:
    ls=[l for l in LINES if l["H"]==h and l["I"]==s]
    if len(ls)<55: continue
    ws=[w for l in ls for w in l["w"]]; store[(h,s)]=(ls,ws)
    ln=[len(w) for w in ws]; mu=mean(ln); sd=(mean([(x-mu)**2 for x in ln]))**0.5
    adj=mean([lcp(a,b) for l in ls for a,b in zip(l["w"],l["w"][1:])])
    ctl=mean([lcp(a,rnd.choice(ALLW)) for l in ls for a in l["w"][:-1]])
    ty=collections.Counter(ws); T=len(ws)
    same=sum(1 for l in ls for a,b in zip(l["w"],l["w"][1:]) if a==b)
    npair=sum(len(l["w"])-1 for l in ls)
    exp=sum((n/T)**2 for n in ty.values())*npair
    def ed1(a,b):
        if a==b or abs(len(a)-len(b))>1: return False
        if len(a)==len(b): return sum(x!=y for x,y in zip(a,b))==1
        x,y=(a,b) if len(a)<len(b) else (b,a)
        return any(y[:i]+y[i+1:]==x for i in range(len(y)))
    e1=sum(1 for l in ls for a,b in zip(l["w"],l["w"][1:]) if ed1(a,b))/npair
    fi=collections.Counter(gl(l["w"][0])[0] for l in ls)
    md=collections.Counter(gl(w)[0] for l in ls for w in l["w"][1:-1])
    Tf=sum(fi.values()); Tm=sum(md.values()) or 1
    div=0.5*sum(abs(fi.get(k,0)/Tf-md.get(k,0)/Tm) for k in set(fi)|set(md))
    lang="".join(sorted({l["L"] for l in ls}))
    print(f"  рука {h} · {SEC[s]:12s} {lang:4s} {T:6d} {mu:6.2f} {sd/mu:5.2f} "
          f"{mean([len(l['w']) for l in ls]):7.2f} {adj-ctl:7.3f} {same/exp:7.2f} {e1:6.1%} {div:8.3f}")

print("\n"+"="*104)
print("ПАНЕЛЬ B — размеро-зависимые меры на РАВНЫХ подвыборках по 6000 слов, 20 повторов")
print("="*104)
big=[(h,s) for h,s in CELLS if (h,s) in store and len(store[(h,s)][1])>=6000]
print(f"  {'ячейка':22s} {'яз':4s} {'h1':>6s} {'h2':>6s} {'слотовость':>11s} {'TTR':>6s} {'хапакс':>7s} {'Ципф':>7s}")
for h,s in big:
    ws=store[(h,s)][1]; acc=collections.defaultdict(list)
    for k in range(20):
        r=random.Random(100+k); sub=r.sample(ws,6000)
        a,b=h12(sub); acc['h1'].append(a); acc['h2'].append(b)
        acc['mi'].append(mi(sub))
        ty=collections.Counter(sub)
        acc['ttr'].append(len(ty)/6000); acc['hap'].append(sum(1 for v in ty.values() if v==1)/len(ty))
        acc['z'].append(zipf(list(ty.values())))
    lang="".join(sorted({l["L"] for l in store[(h,s)][0]}))
    print(f"  рука {h} · {SEC[s]:12s} {lang:4s} {mean(acc['h1']):6.2f} {mean(acc['h2']):6.2f} "
          f"{mean(acc['mi']):11.3f} {mean(acc['ttr']):6.3f} {mean(acc['hap']):7.1%} {mean(acc['z']):7.2f}")
