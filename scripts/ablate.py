import random, collections, json, sys
sys.path.insert(0,".")
import metrics, gens
VOY, LINELENS, LINES = gens.VOY, gens.LINELENS, gens.LINES
T=json.load(open("target.json"))

def composite(p_rep, p_mut, line_layer=True, copy_layer=True, markov=True, seed=1):
    rnd=random.Random(seed)
    s=" ".join(VOY); tr=collections.defaultdict(list)
    for i in range(len(s)-2): tr[s[i:i+2]].append(s[i+2])
    GL="oeyhacdikl".replace(" ",""); 
    def fresh():
        if not markov:                       # слой 1 отключён: случайные буквы нужной длины
            n=max(1,int(rnd.gauss(5.06,1.95)))
            return "".join(rnd.choices("oeyhacdiklrstnqpmf",
                       weights=[25143,20224,17691,17480,14521,12983,12963,11721,10825,10523,7408,7265,6798,6119,5422,1604,1053,463],k=n))
        cur=" "+rnd.choice("oqcdstkyp"); buf=[cur[1]]
        for _ in range(40):
            nx=rnd.choice(tr.get(cur) or [" "])
            if nx==" ": break
            buf.append(nx); cur=cur[1]+nx
        return "".join(buf) or "o"
    fi=collections.Counter(l[0][0] for l in LINES if l); fk=list(fi); fw=[fi[k] for k in fk]
    out=[]; prev=None
    for n in LINELENS:
        line=[]
        for j in range(n):
            if j==0 and line_layer:
                want=rnd.choices(fk,fw)[0]; w=None
                for _ in range(40):
                    c=fresh()
                    if c[0]==want: w=c; break
                w=w or (want+fresh()[1:])
            elif copy_layer and prev and rnd.random()<p_rep: w=prev
            elif copy_layer and prev and rnd.random()<p_mut: w=gens.mutate(prev,rnd)
            else: w=fresh()
            line.append(w); prev=w
        out.append(line)
    return out

VAR=[("все три слоя",           dict()),
     ("без слоя строки",        dict(line_layer=False)),
     ("без копирования слов",   dict(copy_layer=False)),
     ("без марковской формы",   dict(markov=False))]
KEY=[("h2","h2"),("mi_pos","слотовость"),("rep_ratio","повторы ×"),("ed1","отл. в 1 знак"),
     ("zipf","наклон Ципфа"),("line_div","эффект строки"),("wh2","H(слово|пред)")]
print(f"{'вариант':24s}" + "".join(f"{l[:13]:>14s}" for _,l in KEY) + f"{'из 14':>9s}")
print(f"{'ЦЕЛЬ':24s}" + "".join(f"{T[k]:14.3f}" for k,_ in KEY) + f"{'—':>9s}")
print("-"*(24+14*len(KEY)+9))
ALL=[k for k in T]
for name,kw in VAR:
    L=composite(0.004,0.02,**kw); ws=[w for l in L for w in l]
    m=metrics.all_metrics(ws,L)
    hits=sum(1 for k in ALL if abs(m[k]-T[k])/max(abs(T[k]),1e-9)<=0.15)
    print(f"{name:24s}" + "".join(f"{m[k]:14.3f}" for k,_ in KEY) + f"{hits:7d}  ")
