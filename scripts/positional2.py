# -*- coding: utf-8 -*-
import json, collections, math, statistics as st
D=json.load(open("parsed.json"))
LN=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
LN=[l for l in LN if len(l)>=4]
voc=collections.Counter(w for l in LN for w in l)
pos=collections.defaultdict(list)
for l in LN:
    n=len(l)-1
    for i,w in enumerate(l): pos[w].append(i/n if n else 0)
PREF=["s","y","d","o","l","r","q","k","t","a","e","ch","sh","qo","cth","ckh","ok","ot","da","yk","yt","che","she","qok"]
print("="*106)
print("ПОЗИЦИОННАЯ ПРИСТАВКА БЕЗ ГОЛОГО ТОКЕНА: стоит ли PX в строке раньше, чем то же X")
print("="*106)
print(f"  {'P':>5s} {'пар X':>6s} {'токенов PX':>11s} {'сдвиг места':>12s} {'пар «раньше»':>13s} {'p':>9s} {'голых P':>8s}")
rows=[]
for P in PREF:
    pairs=[]
    for X,n in voc.items():
        if n<25: continue
        PX=P+X
        if voc.get(PX,0)>=15:
            pairs.append((X,PX,st.mean(pos[X]),st.mean(pos[PX]),voc[PX]))
    if len(pairs)<5: 
        rows.append((None,P,len(pairs),0,0)); continue
    d=[b-a for _,_,a,b,_ in pairs]         # отрицательное = PX раньше
    earlier=sum(1 for x in d if x<0)
    md=st.mean(d)
    # знаковый тест
    k,nn=earlier,len(d)
    pv=2*sum(math.comb(nn,i)*0.5**nn for i in range(min(k,nn-k)+1))
    ntok=sum(c for _,_,_,_,c in pairs)
    rows.append(((md,earlier,nn,pv,ntok),P,len(pairs),voc.get(P,0),0))
for r,P,npairs,bare,_ in rows:
    if r is None:
        print(f"  {P:>5s} {npairs:6d} {'—':>11s} {'—':>12s} {'—':>13s} {'—':>9s} {voc.get(P,0):8d}   пар мало")
        continue
    md,earlier,nn,pv,ntok=r
    mark=""
    if pv<0.05 and md<0: mark="  ← РАНЬШЕ"
    elif pv<0.05 and md>0: mark="  позже"
    print(f"  {P:>5s} {nn:6d} {ntok:11d} {md:+12.3f} {str(earlier)+'/'+str(nn):>13s} {pv:9.4f} {bare:8d}{mark}")
print("\n  «сдвиг места» — насколько PX в среднем позже X; отрицательное значит раньше в строке")
print("  p — знаковый тест по парам, без предположений о распределении")
