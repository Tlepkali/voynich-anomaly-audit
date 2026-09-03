import json, collections, re, sys
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
def show(ws, lab):
    w=ws[:N]
    if len(w)<N: print(f"  {lab:36s} мало данных ({len(w)})"); return None
    ty=collections.Counter(w); r,s,e=rep(w)
    e1=sum(1 for a,b in zip(w,w[1:]) if ed1(a,b))/(len(w)-1)
    hap=sum(1 for v in ty.values() if v==1)/len(ty)
    print(f"  {lab:36s} {len(ty):5d} {len(ty)/len(w):7.3f} {hap:8.3f} {r:8.3f}× {e1:8.3f} "
          f"{sum(len(x) for x in w)/len(w):8.2f}")
    return r
D=json.load(open("parsed.json")); rows=D["rows"]
VOY=[w for r in rows if r["locus"]=="P" for w in r["words"] if '?' not in w]
TEX=re.compile(r"\\[a-zA-Z]+|[{}]|[a-zA-Z]+|\d+|[^\s]")
tex=TEX.findall(open("ref/latex_math.raw").read())
print("="*104)
print("ЖАНРЫ: травник, рецепты, формулы — против рукописи (по 4000 единиц)")
print("="*104)
print(f"  {'корпус':36s} {'типов':>5s} {'TTR':>7s} {'хапаксы':>8s} {'повторы':>9s} {'отл.1':>8s} {'ср.длина':>8s}")
R={}
R["ВОЙНИЧ"]=show(VOY,"ВОЙНИЧ")
print("  "+"-"*100)
R["травник Калпепера (англ., 1653)"]=show(open("ref/g_herbal.clean").read().split(),"травник Калпепера (англ., 1653)")
R["Апиций — рецепты (латынь)"]=show(open("ref/g_apicius.clean").read().split(),"Апиций — рецепты (латынь)")
R["поваренная книга (англ., XX в.)"]=show(open("ref/g_cookbook.clean").read().split(),"поваренная книга (англ., XX в.)")
R["формулы LaTeX"]=show(tex,"формулы LaTeX")
print("  "+"-"*100)
R["Плиний — латинская проза"]=show(open("ref/latin.clean").read().split(),"Плиний — латинская проза")
R["английская проза"]=show(open("ref/english.clean").read().split(),"английская проза")
print("\n"+"="*104)
print("ПОВТОРЫ СОСЕДНИХ ЕДИНИЦ")
print("="*104)
for k,v in sorted([(k,v) for k,v in R.items() if v is not None], key=lambda kv:-kv[1]):
    print(f"  {k:36s} {v:7.3f}×  {'█'*int(min(v,3)*22)}")
print("\n  самые частые повторы подряд:")
for lab,ws in (("формулы LaTeX",tex),("травник",open("ref/g_herbal.clean").read().split()),
               ("Апиций",open("ref/g_apicius.clean").read().split()),("ВОЙНИЧ",VOY)):
    w=ws[:N]; c=collections.Counter(a for a,b in zip(w,w[1:]) if a==b)
    print(f"     {lab:16s} " + ("  ".join(f"{k}×{v}" for k,v in c.most_common(5)) or "нет"))
