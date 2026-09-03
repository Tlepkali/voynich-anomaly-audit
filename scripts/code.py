import re, glob, sysconfig, collections, random, os, json, sys
sys.path.insert(0,".")
TOK=re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+|[^\sA-Za-z0-9_]")
def load(paths, limit=400000):
    out=[]; n=0
    for p in paths:
        try: t=open(p, encoding="utf-8", errors="replace").read()
        except Exception: continue
        out.append(t); n+=len(t)
        if n>limit: break
    return "\n".join(out)
def tokens(src): return TOK.findall(src)
std=sysconfig.get_paths()["stdlib"]
CORP={}
CORP["python (императивный)"]=tokens(load(sorted(glob.glob(std+"/**/*.py", recursive=True))[:120]))
c=sorted(set(glob.glob("/usr/share/**/*.c", recursive=True))|set(glob.glob("/Library/**/*.c", recursive=True)))[:200]
if len(c)<20: c=[p for p in __import__("subprocess").run(["find","/Library","/usr/share","-name","*.c","-type","f"],capture_output=True,text=True).stdout.split("\n") if p][:200]
CORP["c (императивный)"]=tokens(load(c))
js=[p for p in __import__("subprocess").run(["find","/Library","/usr/share","-name","*.js","-type","f"],capture_output=True,text=True).stdout.split("\n") if p][:200]
CORP["javascript"]=tokens(load(js))
sq=[p for p in __import__("subprocess").run(["find","/Applications","/usr/share","-name","*.sql","-type","f"],capture_output=True,text=True).stdout.split("\n") if p][:60]
CORP["sql (декларативный)"]=tokens(load(sq))
sh=[p for p in __import__("subprocess").run(["find","/usr/share","/etc","-name","*.sh","-type","f"],capture_output=True,text=True).stdout.split("\n") if p][:200]
CORP["shell"]=tokens(load(sh))
N=4000
def rep(w):
    ty=collections.Counter(w); T=len(w)
    same=sum(1 for a,b in zip(w,w[1:]) if a==b)
    exp=sum((n/T)**2 for n in ty.values())*(T-1)
    return same, exp, (same/exp if exp else 0)
print("="*92)
print("ФОРМАЛЬНЫЕ ЗАПИСИ: те же меры, что и на языках (по 4000 токенов)")
print("="*92)
print(f"  {'корпус':26s} {'токенов':>8s} {'ед./токен':>10s} {'TTR':>7s} {'хапаксы':>8s} {'повторы':>10s}")
res={}
for lab,t in CORP.items():
    if len(t)<N: 
        print(f"  {lab:26s} мало данных ({len(t)})"); continue
    w=t[:N]; ty=collections.Counter(w)
    mu=sum(len(x) for x in w)/len(w)
    s,e,r=rep(w); hap=sum(1 for v in ty.values() if v==1)/len(ty)
    res[lab]=r
    print(f"  {lab:26s} {len(w):8d} {mu:10.2f} {len(ty)/len(w):7.3f} {hap:8.3f} {r:9.3f}×")
D=json.load(open("parsed.json")); rows=D["rows"]
VOY=[w for r in rows if r["locus"]=="P" for w in r["words"] if '?' not in w][:N]
ty=collections.Counter(VOY); s,e,r=rep(VOY)
res["ВОЙНИЧ"]=r
print(f"  {'ВОЙНИЧ':26s} {len(VOY):8d} {sum(len(x) for x in VOY)/len(VOY):10.2f} "
      f"{len(ty)/len(VOY):7.3f} {sum(1 for v in ty.values() if v==1)/len(ty):8.3f} {r:9.3f}×")
print("\n" + "="*92)
print("ПОВТОРЫ СОСЕДНИХ ЕДИНИЦ — единственная мера, где Войнич был одинок")
print("="*92)
for k,v in sorted(res.items(), key=lambda kv:-kv[1]):
    print(f"  {k:26s} {v:8.3f}×  {'█'*int(min(v,4)*16)}")
