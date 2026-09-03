import json, collections, random, itertools, sys, re, subprocess
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows=D["rows"]
VL=[[w for w in r["words"] if '?' not in w] for r in rows if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]
LENS=[]; tot=0
for l in VL:
    if tot>=4000: break
    LENS.append(len(l)); tot+=len(l)
N=tot
VOY=[w for l in VL for w in l][:N]
LET="BCDEFGHIK"          # девять букв Луллия: B..K без J
def lay(words):
    out=[]; k=0
    for n in LENS:
        if k+n>len(words): break
        out.append(words[k:k+n]); k+=n
    return out
def M(words):
    L=lay(words)
    return metrics.all_metrics([w for l in L for w in l], L)

GEN={}
# 1. Строгая четвёртая фигура: три диска по девять букв, поворот ПО ОДНОМУ диску
def fig4_rotate(n, seed=1):
    rnd=random.Random(seed); st=[0,0,0]; out=[]
    for _ in range(n):
        out.append("".join(LET[i] for i in st))
        w=rnd.randrange(3); st[w]=(st[w]+rnd.randrange(1,9))%9
    return out
GEN["Луллий: 3 диска, поворот по одному"]=fig4_rotate(N)
# 2. То же, но все три диска сразу (случайная выдача)
def fig4_random(n, seed=2):
    rnd=random.Random(seed)
    return ["".join(rnd.choice(LET) for _ in range(3)) for _ in range(n)]
GEN["Луллий: 3 диска, все сразу"]=fig4_random(N)
# 3. С шестью столбцами значений: буква+столбец на каждом диске
def fig4_columns(n, seed=3):
    rnd=random.Random(seed); st=[(0,0)]*3; out=[]
    for _ in range(n):
        out.append("".join(LET[a]+"abcdef"[b] for a,b in st))
        w=rnd.randrange(3)
        st=list(st); st[w]=(rnd.randrange(9), rnd.randrange(6)); st=tuple(st)
    return out
GEN["Луллий: 3 диска × 6 столбцов"]=fig4_columns(N)
# 4. Обобщённая машина, подогнанная под объём словаря рукописи: 5 дисков по 6 знаков
def wheels(n, k, m, seed=4, rotate=True):
    rnd=random.Random(seed); alpha=[chr(97+i) for i in range(m)]
    st=[0]*k; out=[]
    for _ in range(n):
        out.append("".join(alpha[i] for i in st))
        if rotate:
            w=rnd.randrange(k); st[w]=(st[w]+rnd.randrange(1,m))%m
        else:
            st=[rnd.randrange(m) for _ in range(k)]
    return out
GEN["Обобщённая: 5 дисков × 6, по одному"]=wheels(N,5,6)
GEN["Обобщённая: 5 дисков × 6, все сразу"]=wheels(N,5,6,rotate=False)

print("="*104)
print("СТАТИСТИКА ЛУЛЛИЕВОЙ МАШИНЫ ПРОТИВ РУКОПИСИ (по 4000 слов)")
print("="*104)
KEYS=[("mean_len","ср.длина"),("ttr","TTR"),("hapax","хапаксы"),("rep_ratio","повторы ×"),
      ("ed1","отл. в 1 знак"),("h2","h2"),("mi_pos","слотовость"),("zipf","Ципф")]
mv=M(VOY)
print(f"  {'корпус':34s} {'типов':>6s} " + " ".join(f"{l:>10s}" for _,l in KEYS))
print(f"  {'РУКОПИСЬ ВОЙНИЧА':34s} {len(set(VOY)):6d} " +
      " ".join(f"{mv[k]:10.3f}" for k,_ in KEYS))
print("  " + "-"*100)
for lab,ws in GEN.items():
    m=M(ws)
    print(f"  {lab:34s} {len(set(ws)):6d} " + " ".join(f"{m[k]:10.3f}" for k,_ in KEYS))

print("\n" + "="*104)
print("РАЗМЕТКА: HTML, XML, plist — версия «древний html»")
print("="*104)
TOK=re.compile(r"[A-Za-z_][A-Za-z0-9_-]*|\d+|[^\sA-Za-z0-9_]")
def find(root, ext, k=150):
    return [p for p in subprocess.run(["find",root,"-name",f"*.{ext}","-type","f"],
            capture_output=True,text=True).stdout.split("\n") if p][:k]
def load(paths, lim=500000):
    o=[]; n=0
    for p in paths:
        try: t=open(p, encoding="utf-8", errors="replace").read()
        except Exception: continue
        o.append(t); n+=len(t)
        if n>lim: break
    return "\n".join(o)
for lab, paths in (("HTML", find("/Library","html")+find("/usr/share","html")),
                   ("XML / plist", find("/Library","plist",100)+find("/usr/share","xml",100))):
    t=TOK.findall(load(paths))
    if len(t)<N: print(f"  {lab}: мало данных ({len(t)})"); continue
    w=t[:N]; ty=collections.Counter(w)
    same=sum(1 for a,b in zip(w,w[1:]) if a==b)
    exp=sum((n/len(w))**2 for n in ty.values())*(len(w)-1)
    hap=sum(1 for v in ty.values() if v==1)/len(ty)
    print(f"  {lab:14s} типов {len(ty):5d}  TTR {len(ty)/len(w):.3f}  хапаксы {hap:.3f}  "
          f"повторы {same/exp:6.3f}×  ср.длина {sum(len(x) for x in w)/len(w):.2f}")
print(f"  {'ВОЙНИЧ':14s} типов {len(set(VOY)):5d}  TTR {mv['ttr']:.3f}  хапаксы {mv['hapax']:.3f}  "
      f"повторы {mv['rep_ratio']:6.3f}×  ср.длина {mv['mean_len']:.2f}")
