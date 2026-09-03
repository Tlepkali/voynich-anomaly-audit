# -*- coding: utf-8 -*-
import json, collections, statistics as st, math
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]
LENS=[len(l) for l in VL]
lw=open("ref/latin.clean").read().split(); LL=[];p=0
for n in LENS:
    if p+n>len(lw): break
    LL.append(lw[p:p+n]); p+=n
def corr_pairs(P):
    xs=[a for a,_ in P]; ys=[b for _,b in P]
    mx,my=st.mean(xs),st.mean(ys)
    num=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
    den=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    return num/den if den else 0
def impl_A(L):   # ранги по частоте, ties разрешаются порядком most_common
    f=[w for l in L for w in l]
    c=collections.Counter(f); rk={w:i+1 for i,(w,_) in enumerate(c.most_common())}
    return corr_pairs([(math.log(rk[l[i]]),math.log(rk[l[i+1]])) for l in L for i in range(len(l)-1)])
def impl_B(L):   # то же, но ранг = СРЕДНИЙ ранг внутри группы одинаковой частоты
    f=[w for l in L for w in l]
    c=collections.Counter(f); items=c.most_common()
    rk={}; i=0
    while i<len(items):
        j=i
        while j<len(items) and items[j][1]==items[i][1]: j+=1
        avg=(i+1+j)/2
        for k in range(i,j): rk[items[k][0]]=avg
        i=j
    return corr_pairs([(math.log(rk[l[i]]),math.log(rk[l[i+1]])) for l in L for i in range(len(l)-1)])
def impl_C(L):   # по ЛОГ-ЧАСТОТЕ вместо ранга — без проблемы ties вообще
    f=[w for l in L for w in l]; c=collections.Counter(f)
    return corr_pairs([(math.log(c[l[i]]),math.log(c[l[i+1]])) for l in L for i in range(len(l)-1)])
print(f"  {'корпус':>10s} {'A: ранг как есть':>18s} {'B: средний ранг':>17s} {'C: лог-частота':>16s}")
for nm,L in [("Войнич",VL),("латынь",LL)]:
    print(f"  {nm:>10s} {impl_A(L):18.4f} {impl_B(L):17.4f} {impl_C(L):16.4f}")
print("\n  сколько слов с частотой 1 (там ties максимальны):")
for nm,L in [("Войнич",VL),("латынь",LL)]:
    c=collections.Counter(w for l in L for w in l)
    h=sum(1 for v in c.values() if v==1)
    print(f"    {nm}: типов {len(c)}, из них однократных {h} = {h/len(c):.0%}")
