# -*- coding: utf-8 -*-
import json, collections, math, statistics as st
D=json.load(open("parsed.json"))
LN=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
LN=[l for l in LN if len(l)>=4]
voc=collections.Counter(w for l in LN for w in l)
pos=collections.defaultdict(list); bylen=collections.defaultdict(list)
for l in LN:
    n=len(l)-1
    for i,w in enumerate(l):
        p=i/n if n else 0
        pos[w].append(p); bylen[len(w)].append(p)
LP={k:st.mean(v) for k,v in bylen.items() if len(v)>=100}
SUF=["m","am","g","y","n","r","l","s","o","d","dy","in","iin","aiin","ain","ar","or","al","ol","edy","eey","ey","chy","hy","od","am","oiin"]
print("="*104)
print("ЗЕРКАЛЬНЫЙ ТЕСТ: приписывается ли элемент в КОНЦЕ строки (XS позже, чем X)")
print("="*104)
print(f"  {'S':>6s} {'пар':>4s} {'ток. XS':>8s} {'набл.':>8s} {'по длине':>9s} {'ИЗБЫТОК':>9s} {'пар позже':>10s} {'p':>8s} {'голых S':>8s}")
seen=set()
for S in SUF:
    if S in seen: continue
    seen.add(S)
    pairs=[]
    for X,n in voc.items():
        if n<25: continue
        XS=X+S
        if voc.get(XS,0)>=15 and len(X) in LP and len(XS) in LP:
            pairs.append((st.mean(pos[XS])-st.mean(pos[X]), LP[len(XS)]-LP[len(X)], voc[XS]))
    if len(pairs)<5:
        print(f"  {S:>6s} {len(pairs):4d} {'—':>8s} {'—':>8s} {'—':>9s} {'—':>9s} {'—':>10s} {'—':>8s} {voc.get(S,0):8d}")
        continue
    ex=[a-b for a,b,_ in pairs]
    k=sum(1 for x in ex if x>0); nn=len(ex)
    pv=2*sum(math.comb(nn,i)*0.5**nn for i in range(min(k,nn-k)+1))
    pv=min(pv,1.0)
    o=st.mean([a for a,_,_ in pairs]); e=st.mean([b for _,b,_ in pairs])
    tok=sum(c for _,_,c in pairs)
    mark=""
    if pv<0.05 and st.mean(ex)>0: mark="  ← ПОЗЖЕ"
    elif pv<0.05 and st.mean(ex)<0: mark="  раньше"
    print(f"  {S:>6s} {nn:4d} {tok:8d} {o:+8.3f} {e:+9.3f} {st.mean(ex):+9.3f} {str(k)+'/'+str(nn):>10s} {pv:8.4f} {voc.get(S,0):8d}{mark}")
