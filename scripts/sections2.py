# -*- coding: utf-8 -*-
import json, collections, random, statistics as st
D=json.load(open("parsed.json")); PG=D["pages"]
NAME={"H":"травник","B":"«банный»","S":"звёзды","T":"текст","C":"космология","P":"аптечный"}
sec=collections.defaultdict(list)
for r in D["rows"]:
    if r["locus"]!="P": continue
    m=PG.get(r["page"],{}); ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=2: sec[(m.get("I","?"),m.get("L","?"))].append(ws)
def pool(s,L=None): return [l for (a,b),v in sec.items() if a==s and (L is None or b==L) for l in v]
def adj_ratio(lines,seed=0):
    obs=sum(1 for l in lines for i in range(len(l)-1) if l[i]==l[i+1])
    rnd=random.Random(seed); acc=0.0; R=20
    for _ in range(R):
        for l in lines:
            p=rnd.sample(l,len(l)); acc+=sum(1 for a,b in zip(p,p[1:]) if a==b)
    return obs, acc/R
def boot_adj(lines,B=300):
    rnd=random.Random(11); out=[]
    for b in range(B):
        s=[lines[rnd.randrange(len(lines))] for _ in range(len(lines))]
        o,e=adj_ratio(s,seed=b)
        if e>0.5: out.append(o/e)
    out.sort(); return out[int(.025*len(out))], out[int(.975*len(out))]
def matched(lines,N,B=40,seed=5):
    rnd=random.Random(seed); ttr=[]; hap=[]
    for _ in range(B):
        sh=lines[:]; rnd.shuffle(sh); f=[]
        for l in sh:
            f+=l
            if len(f)>=N: break
        if len(f)<N: continue
        f=f[:N]; c=collections.Counter(f)
        ttr.append(len(c)/N); hap.append(sum(1 for v in c.values() if v==1)/len(c))
    return st.mean(ttr), st.mean(hap)
print("="*100); print("ВЫРОВНЕННЫЙ ОБЪЁМ: TTR и хапаксы на 2000 слов (40 подвыборок)"); print("="*100)
print(f"  {'раздел':>13s} {'всего':>7s} {'TTR@2k':>8s} {'хапакс@2k':>10s} {'соседство':>10s} {'95% ДИ':>16s}")
rows=[]
for s in ["S","H","B","P","T"]:
    L=pool(s); n=sum(len(l) for l in L)
    t,h=matched(L,2000); o,e=adj_ratio(L); lo,hi=boot_adj(L)
    rows.append((s,n,t,h,o/e,lo,hi))
    print(f"  {NAME[s]:>13s} {n:7,d} {t:8.3f} {h:10.1%} {o/e:9.2f}× [{lo:5.2f}; {hi:5.2f}]")
print("\n"+"="*100); print("ТОЛЬКО ЯЗЫК B, ВЫРОВНЕННЫЙ ОБЪЁМ 2000 СЛОВ"); print("="*100)
print(f"  {'раздел':>13s} {'слов B':>7s} {'TTR@2k':>8s} {'хапакс@2k':>10s} {'соседство':>10s} {'95% ДИ':>16s}")
for s in ["S","B","H","T"]:
    L=pool(s,"B"); n=sum(len(l) for l in L)
    if n<2000: continue
    t,h=matched(L,2000); o,e=adj_ratio(L); lo,hi=boot_adj(L)
    print(f"  {NAME[s]:>13s} {n:7,d} {t:8.3f} {h:10.1%} {o/e:9.2f}× [{lo:5.2f}; {hi:5.2f}]")
print("\n"+"="*100); print("СЛОВАРНОЕ ПЕРЕСЕЧЕНИЕ РАЗДЕЛОВ (Жаккар по типам, выровнено 2000 слов)"); print("="*100)
def types(s,L,N=2000,seed=7):
    ls=pool(s,L); rnd=random.Random(seed); rnd.shuffle(ls); f=[]
    for l in ls:
        f+=l
        if len(f)>=N: break
    return set(f[:N]) if len(f)>=N else None
G=[("S","B"),("B","B"),("H","B"),("T","B"),("H","A"),("P","A")]
lab=[f"{NAME[s]}/{L}" for s,L in G]; T=[types(s,L) for s,L in G]
print("  "+" "*15+" ".join(f"{x:>13s}" for x in lab))
for i,a in enumerate(T):
    cells=[]
    for j,b in enumerate(T):
        cells.append("      —      " if a is None or b is None else f"{len(a&b)/len(a|b):13.3f}")
    print(f"  {lab[i]:>15s}"+" ".join(cells))
