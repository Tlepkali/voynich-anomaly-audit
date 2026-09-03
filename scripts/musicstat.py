import json, collections, re, math, sys
sys.path.insert(0,".")
N=4000
def rep(w):
    ty=collections.Counter(w); T=len(w)
    same=sum(1 for a,b in zip(w,w[1:]) if a==b)
    exp=sum((n/T)**2 for n in ty.values())*(T-1)
    return (same/exp if exp else 0), same, exp
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
def show(ws, lab):
    w=ws[:N]
    if len(w)<N: print(f"  {lab:32s} мало ({len(w)})"); return None
    ty=collections.Counter(w); r,s,e=rep(w)
    e1=sum(1 for a,b in zip(w,w[1:]) if ed1(a,b))/(len(w)-1)
    hap=sum(1 for v in ty.values() if v==1)/len(ty)
    print(f"  {lab:32s} {len(ty):5d} {len(ty)/len(w):7.3f} {hap:8.3f} {r:8.3f}× {e1:7.3f} "
          f"{sum(len(x) for x in w)/len(w):8.2f} {mi_pos(w):9.3f}")
    return r
# разбор kern: ноты — это поля строк данных
notes=[]
for line in open("ref/music_kern.raw"):
    line=line.rstrip("\n")
    if not line or line[0] in "!*=": continue
    for f in line.split("\t"):
        f=f.strip()
        if f and f!="." and not f.startswith("!"):
            notes.append(f)
print(f"  нотных единиц: {len(notes):,}, различных: {len(set(notes)):,}")
print(f"  пример: {' '.join(notes[40:56])}\n")
D=json.load(open("parsed.json")); rows=D["rows"]
VOY=[w for r in rows if r["locus"]=="P" for w in r["words"] if '?' not in w]
print("="*104)
print("НОТНАЯ ЗАПИСЬ XV–XVI вв. ПРОТИВ РУКОПИСИ (по 4000 единиц)")
print("="*104)
print(f"  {'корпус':32s} {'типов':>5s} {'TTR':>7s} {'хапаксы':>8s} {'повторы':>9s} {'отл.1':>7s} {'ср.длина':>8s} {'слотовость':>9s}")
R={}
R["ВОЙНИЧ"]=show(VOY,"ВОЙНИЧ")
R["нотация (Жоскен и др.)"]=show(notes,"нотация (Жоскен, Окегем и др.)")
R["только высоты (без длительностей)"]=show([re.sub(r"[\d.]","",n) or "r" for n in notes],
                                             "  только высоты")
R["только длительности"]=show([re.sub(r"[^\d.]","",n) or "x" for n in notes],
                               "  только длительности")
R["Плиний"]=show(open("ref/latin.clean").read().split(),"Плиний — латинская проза")
print("\n  что повторяется подряд:")
for lab,ws in (("нотация",notes),("ВОЙНИЧ",VOY)):
    w=ws[:N]; c=collections.Counter(a for a,b in zip(w,w[1:]) if a==b)
    print(f"     {lab:12s} " + "  ".join(f"{k}×{v}" for k,v in c.most_common(6)))
