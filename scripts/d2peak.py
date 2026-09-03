import json, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows, pages = D["rows"], D["pages"]
P=[r for r in rows if r["locus"]=="P"]
LINES=[]
for r in P:
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=3:
        LINES.append({"w":ws,"L":pages.get(r["page"],{}).get("L","?")})

def lcp(a,b):
    ga,gb=metrics.merge(a),metrics.merge(b); n=0
    for x,y in zip(ga,gb):
        if x!=y: break
        n+=1
    return n
def eds(a,b):
    ga,gb=metrics.merge(a),metrics.merge(b); la,lb=len(ga),len(gb)
    prev=list(range(lb+1))
    for i in range(1,la+1):
        cur=[i]+[0]*lb
        for j in range(1,lb+1):
            cur[j]=min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ga[i-1]!=gb[j-1]))
        prev=cur
    return 1-prev[lb]/max(la,lb)

def per_line_delta(lines, f, dA, dB, interior=False):
    """для каждой строки: средняя разность sim(i,i+dB) − sim(i,i+dA) при общем якоре i"""
    out=[]
    for l in lines:
        w=l["w"]; n=len(w); vals=[]
        lo = 1 if interior else 0
        hi = n-1 if interior else n
        for i in range(lo, hi):
            if i+max(dA,dB) >= hi: break
            vals.append(f(w[i],w[i+dB]) - f(w[i],w[i+dA]))
        if vals: out.append(sum(vals)/len(vals))
    return out

def boot_mean(vals, n=4000, seed=11):
    rnd=random.Random(seed); N=len(vals); res=[]
    for _ in range(n):
        res.append(sum(vals[rnd.randrange(N)] for _ in range(N))/N)
    res.sort(); return sum(vals)/N, res[int(.025*n)], res[int(.975*n)]

def shuffled(lines, seed=5):
    rnd=random.Random(seed)
    out=[]
    for l in lines:
        w=l["w"][:]; rnd.shuffle(w); out.append({"w":w,"L":l["L"]})
    return out

for measure_name, f in (("общий начальный кусок", lcp), ("похожесть по правке", eds)):
    print("="*80)
    print(f"МЕРА: {measure_name}.  Разность sim(i,i+2) − sim(i,i+1) при общем якоре i")
    print("бутстрэп по СТРОКАМ, 4000 повторов")
    print("="*80)
    for lang in ("A","B"):
        ls=[l for l in LINES if l["L"]==lang]
        for tag, interior in (("все слова",False),("без краёв строки",True)):
            real=per_line_delta(ls, f, 1, 2, interior)
            ctl =per_line_delta(shuffled(ls), f, 1, 2, interior)
            m,lo,hi = boot_mean(real)
            mc,loc,hic = boot_mean(ctl, seed=17)
            star = "ЗНАЧИМО" if (lo>0 or hi<0) else "не значимо"
            print(f"  {lang} · {tag:18s} строк {len(real):5d}   "
                  f"разность {m:+.4f} [{lo:+.4f}, {hi:+.4f}]  {star:11s}"
                  f"  контроль {mc:+.4f} [{loc:+.4f}, {hic:+.4f}]")
        print()

print("="*80)
print("ЕСЛИ ЭТО ЦИКЛ ДЛИНЫ 2, чётные расстояния должны быть выше нечётных")
print("="*80)
for lang in ("A","B"):
    ls=[l for l in LINES if l["L"]==lang]
    print(f"  {lang}:")
    for dA,dB in ((1,2),(3,2),(3,4),(5,4)):
        real=per_line_delta(ls, lcp, dA, dB)
        if len(real)<200: continue
        m,lo,hi=boot_mean(real, n=2000, seed=23)
        star="✓" if lo>0 else ("✗" if hi<0 else "·")
        print(f"     d={dB} против d={dA}:  {m:+.4f} [{lo:+.4f}, {hi:+.4f}]  {star}")
