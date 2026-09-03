# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VOY=[w for l in VL for w in l]
N_TYPES=5000; K_AFF=15
def topN(words,n=N_TYPES):
    c=collections.Counter(words); return [w for w,_ in c.most_common(n)]
def affixes(types,k=K_AFF):
    pre=collections.Counter(); suf=collections.Counter()
    for w in types:
        for L in (1,2,3):
            if len(w)>L: pre[w[:L]]+=1; suf[w[-L:]]+=1
    return [a for a,_ in pre.most_common(k)], [a for a,_ in suf.most_common(k)]
def decompose(types):
    S=set(types); P,U=affixes(types)
    derived={}; 
    for w in sorted(S,key=len):
        for a in P:
            if w.startswith(a) and w[len(a):] in S and len(w[len(a):])>=2: derived[w]=("pre",a,w[len(a):]); break
        if w in derived: continue
        for a in U:
            if w.endswith(a) and w[:-len(a)] in S and len(w[:-len(a)])>=2: derived[w]=("suf",a,w[:-len(a)]); break
    cores=[w for w in S if w not in derived]
    # глубина: сколько раз слово сводится, пока не упрётся в ядро
    def depth(w,seen=None):
        seen=seen or set(); d=0
        while w in derived and w not in seen:
            seen.add(w); w=derived[w][2]; d+=1
        return d,w
    dep=[depth(w)[0] for w in S]
    return derived, cores, dep, P, U
def nbrs(T):
    idx=collections.defaultdict(set)
    for w in T:
        idx[w].add(w)
        for i in range(len(w)): idx[w[:i]+w[i+1:]].add(w)
    nb=collections.defaultdict(set)
    for k,ws in idx.items():
        ws=list(ws)
        for i in range(len(ws)):
            for j in range(i+1,len(ws)):
                a,b=ws[i],ws[j]
                if abs(len(a)-len(b))<=1: nb[a].add(b); nb[b].add(a)
    return nb
def shape(T):
    T=set(T); nb=nbrs(T)
    def m(d):
        g=[len(nb.get(w,())) for w in T if len(w)==d]
        return (st.mean(g),len(g)) if len(g)>=15 else (float('nan'),len(g))
    a,na=m(3); b,nb_=m(5)
    return a,na,b,nb_,(b/a if a==a and b==b and a>0 else float('nan'))
def shuf_types(types,seed=0):
    rnd=random.Random(seed); out=set()
    for w in types:
        c=list(w); rnd.shuffle(c); out.add("".join(c))
    return sorted(out)
CORP=[("Войнич",topN(VOY))]
for nm,fn in [("латынь","latin"),("английский","english"),("немецкий","wiki_de"),("итальянский","wiki_it")]:
    p="ref/%s.clean"%fn
    if os.path.exists(p): CORP.append((nm,topN(open(p).read().split())))
sys.path.insert(0,"scripts"); sys.path.insert(0,".")
exec(open("scripts/oos.py").read().split("CORP=")[0])
M=model()
if M: CORP.append(("МОДЕЛЬ",topN([w for l in M for w in l])))
CORP.append(("Войнич, знаки в слове перемешаны",shuf_types(topN(VOY))))
print("="*118); print(f"РАЗЛОЖЕНИЕ НА ЯДРО И ОБВЕС (по {N_TYPES} самых частых типов, по {K_AFF} приставок и {K_AFF} окончаний, отобранных одинаково)"); print("="*118)
print(f"  {'корпус':>32s} {'типов':>6s} {'выводимых':>10s} {'ядер':>6s} {'глуб.≥2':>8s} {'ср.глуб':>8s}")
RES={}
for lab,T in CORP:
    d,c,dep,P,U=decompose(T); RES[lab]=(d,c,T)
    print(f"  {lab:>32s} {len(T):6d} {len(d)/len(T):10.1%} {len(c):6d} {sum(1 for x in dep if x>=2)/len(dep):8.1%} {st.mean(dep):8.2f}")
print("\n"+"="*118); print("ГЛАВНАЯ ПРОВЕРКА: становится ли профиль плотности языковым после снятия обвеса"); print("="*118)
print(f"  {'корпус':>32s} | {'ВСЕ ТИПЫ: дл3':>13s} {'дл5':>7s} {'дл5/дл3':>8s} | {'ЯДРА: дл3':>10s} {'(n)':>6s} {'дл5':>7s} {'(n)':>5s} {'дл5/дл3':>8s}")
for lab,T in CORP:
    d,c,_=RES[lab]
    a,na,b,nb_,r1=shape(T); a2,na2,b2,nb2,r2=shape(c)
    f=lambda x: f"{x:7.1f}" if x==x else "      —"
    g=lambda x: f"{x:8.2f}" if x==x else "       —"
    print(f"  {lab:>32s} | {f(a):>13s} {f(b)} {g(r1)} | {f(a2):>10s} {na2:6d} {f(b2)} {nb2:5d} {g(r2)}")
print("\n  ПРЕДСКАЗАНИЕ: если ровный профиль рукописи (0,81) создаётся обвесом, у ядер он должен стать")
print("  языковым (около 0,2–0,3). Если останется ровным — обвес аномалию не объясняет.")
print("\n"+"="*118); print("ЧТО ЗА ПРИСТАВКИ И ОКОНЧАНИЯ ОТОБРАЛИСЬ У РУКОПИСИ"); print("="*118)
d,c,T=RES["Войнич"]; P,U=affixes(T)
print("  приставки:", " ".join(P)); print("  окончания:", " ".join(U))
cnt=collections.Counter(v[1] for v in d.values() if v[0]=="pre")
cnt2=collections.Counter(v[1] for v in d.values() if v[0]=="suf")
print("  чаще всего снимается спереди:", ", ".join(f"{a}·{n}" for a,n in cnt.most_common(6)))
print("  чаще всего снимается сзади  :", ", ".join(f"{a}·{n}" for a,n in cnt2.most_common(6)))
