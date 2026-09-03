import json, collections, re, sys
sys.path.insert(0,".")
N=4000
lat=open("ref/latin.clean").read().split()
D=json.load(open("parsed.json")); rows=D["rows"]
VOY=[w for r in rows if r["locus"]=="P" for w in r["words"] if '?' not in w][:N]
VOW=set("aeiou")
END=[("orum","%"),("arum","%"),("ibus","&"),("ntur","~"),("tion","+"),("que","q"),
     ("bus","&"),("rum","%"),("tur","~"),("ent","^"),("ius","$"),("um","u"),("us","'"),
     ("is","i"),("es","e"),("am","a"),("em","e"),("as","a"),("os","o")]
def suspension(w, k=3):           # обрубание: только начало слова
    return w[:k]
def nasal(w):                     # титло: снимаем m/n перед согласной
    o=[]
    for i,c in enumerate(w):
        if c in "mn" and i+1<len(w) and w[i+1] not in VOW: continue
        o.append(c)
    return "".join(o) or w[0]
def contraction(w):               # стяжение: первая, последние, скелет согласных
    if len(w)<=3: return w
    core="".join(c for c in w[1:-1] if c not in VOW)
    return (w[0]+core+w[-1])[:6] or w
def endings(w):                   # значки для частых окончаний
    for e,s in END:
        if w.endswith(e) and len(w)>len(e)+1: return w[:-len(e)]+s
    return w
def full(w):                      # всё вместе, как в настоящей рукописи
    return endings(nasal(contraction(w)))
SCHEMES={"без сокращений":lambda w:w,
         "титло (m/n перед согласной)":nasal,
         "значки окончаний":endings,
         "стяжение (скелет согласных)":contraction,
         "обрубание до 3 знаков":lambda w:suspension(w,3),
         "обрубание до 4 знаков":lambda w:suspension(w,4),
         "всё вместе":full}
def rep(w):
    ty=collections.Counter(w); T=len(w)
    same=sum(1 for a,b in zip(w,w[1:]) if a==b)
    exp=sum((n/T)**2 for n in ty.values())*(T-1)
    return (same/exp if exp else 0)
def mi_pos(ws):
    import math
    j=collections.Counter()
    for w in ws:
        for i,c in enumerate(w):
            p="1" if len(w)==1 else ("b" if i==0 else ("e" if i==len(w)-1 else "m"))
            j[(c,p)]+=1
    T=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (a,b),n in j.items(): pg[a]+=n; pp[b]+=n
    return sum(n/T*math.log2((n/T)/((pg[a]/T)*(pp[b]/T))) for (a,b),n in j.items())
def show(ws, lab):
    w=ws[:N]; ty=collections.Counter(w)
    hap=sum(1 for v in ty.values() if v==1)/len(ty)
    print(f"  {lab:30s} {len(ty):5d} {len(ty)/len(w):7.3f} {hap:8.3f} {rep(w):8.3f}× "
          f"{sum(len(x) for x in w)/len(w):8.2f} {mi_pos(w):9.3f}")
print("="*94)
print("ГИПОТЕЗА СОКРАЩЕНИЙ: сокращаем латынь по средневековым правилам")
print("="*94)
print(f"  {'схема':30s} {'типов':>5s} {'TTR':>7s} {'хапаксы':>8s} {'повторы':>9s} {'ср.длина':>8s} {'слотовость':>9s}")
show(VOY,"РУКОПИСЬ ВОЙНИЧА")
print("  "+"-"*90)
for lab,f in SCHEMES.items():
    show([f(w) for w in lat], lab)
