# -*- coding: utf-8 -*-
import json, collections, random, statistics as st
D=json.load(open("parsed.json")); PG=D["pages"]
sec=collections.defaultdict(list)
for r in D["rows"]:
    if r["locus"]!="P": continue
    m=PG.get(r["page"],{}); ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=2 and m.get("L")=="B": sec[m.get("I","?")].append((r["page"],ws))
def pagettr(s):
    byp=collections.defaultdict(list)
    for p,l in sec[s]: byp[p]+=l
    out=[]
    for p,f in byp.items():
        if len(f)<250: continue
        rnd=random.Random(9); v=[st.mean([len(set(f[i:i+250]))/250]) for i in [rnd.randrange(0,len(f)-249) for _ in range(10)]]
        out.append(st.mean(v))
    return sorted(out)
B=pagettr("B"); S=pagettr("S")
print(f"«банный» {len(B)} стр: {B[0]:.3f}..{B[-1]:.3f}   звёзды {len(S)} стр: {S[0]:.3f}..{S[-1]:.3f}")
pairs=sum(1 for b in B for s in S if b<s)
print(f"доля пар (страница «банного» < страница звёзд): {pairs}/{len(B)*len(S)} = {pairs/(len(B)*len(S)):.1%}   ← мера Манна–Уитни")
print(f"страниц звёзд ниже максимума «банного» ({B[-1]:.3f}): {sum(1 for s in S if s<B[-1])} из {len(S)}")
print(f"страниц «банного» выше минимума звёзд ({S[0]:.3f}): {sum(1 for b in B if b>S[0])} из {len(B)}")
