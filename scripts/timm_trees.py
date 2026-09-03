# -*- coding: utf-8 -*-
import json, collections, math, os, statistics as st, random
def neighbours(types):
    """соседи на расстоянии правки 1, через хеш удалений"""
    idx=collections.defaultdict(set)
    for w in types:
        idx[w].add(w)
        for i in range(len(w)): idx[w[:i]+w[i+1:]].add(w)
    nb=collections.defaultdict(set)
    for k,ws in idx.items():
        ws=list(ws)
        if len(ws)<2: continue
        for i in range(len(ws)):
            for j in range(i+1,len(ws)):
                a,b=ws[i],ws[j]
                if abs(len(a)-len(b))>1: continue
                nb[a].add(b); nb[b].add(a)
    return nb
def corr(x,y):
    n=len(x); mx=sum(x)/n; my=sum(y)/n
    c=sum((a-mx)*(b-my) for a,b in zip(x,y))
    d=math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
    return c/d if d else 0.0
def part(rxy,rxz,ryz): return (rxy-rxz*ryz)/math.sqrt(max(1e-12,(1-rxz**2)*(1-ryz**2)))
def analyse(words, lab, cap=8000):
    f=collections.Counter(words)
    types=[w for w,n in f.items() if n>=2]
    if len(types)>cap: types=sorted(types, key=lambda w:-f[w])[:cap]
    T=set(types)
    nb=neighbours(T)
    lf=[math.log(f[w]) for w in types]
    nn=[len(nb.get(w,())) for w in types]
    ln=[len(w) for w in types]
    r_fn=corr(lf,nn); r_ln=corr(ln,nn); r_lf=corr(ln,lf)
    return lab, len(types), r_fn, part(r_fn,r_ln,r_lf), st.mean(nn)
D=json.load(open("parsed.json"))
VOY=[w for r in D["rows"] if r["locus"]=="P" for w in r["words"] if '?' not in w]
print("="*100)
print("КОНТРОЛЬ 1: «частые слова имеют больше похожих» — свойство рукописи или всех текстов?")
print("="*100)
print(f"  {'корпус':>16s} {'типов':>7s} {'связь частота↔соседи':>22s} {'при фикс. длине':>18s} {'соседей в среднем':>18s}")
rows=[analyse(VOY,"Войнич")]
for tag,lab in (("latin","латынь"),("english","английский"),("wiki_de","немецкий"),("wiki_it","итальянский")):
    p=f"ref/{tag}.clean"
    if os.path.exists(p): rows.append(analyse(open(p).read().split(),lab))
for lab,nt,a,b,m in rows:
    mark="  ←" if lab=="Войнич" else ""
    print(f"  {lab:>16s} {nt:7d} {a:21.3f} {b:18.3f} {m:17.2f}{mark}")
print("\n  «при фикс. длине» — частная корреляция с поправкой на длину слова")
