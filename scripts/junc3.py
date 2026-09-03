# -*- coding: utf-8 -*-
import json, collections, math, os, random
D=json.load(open("parsed.json"))
LN=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
LN=[l for l in LN if len(l)>=2]
def cells(lines):
    J=collections.Counter(); A=collections.Counter(); B=collections.Counter()
    for l in lines:
        for x,y in zip(l,l[1:]):
            J[(x[-1],y[0])]+=1; A[x[-1]]+=1; B[y[0]]+=1
    return J,A,B
J,A,B=cells(LN); T=sum(J.values())
def mi_cells(J,A,B,T):
    out=[]
    for (a,b),n in J.items():
        e=A[a]*B[b]/T
        out.append((n/T*math.log2((n/T)/((A[a]/T)*(B[b]/T))), a,b,n,e))
    return out
MC=mi_cells(J,A,B,T); MI=sum(x[0] for x in MC)
print("="*104)
print("ИЗ ЧЕГО СДЕЛАН СТЫК: запреты или градиент")
print("="*104)
print(f"  всего стыков {T:,}, разных сочетаний «последняя буква → первая» {len(J)} из возможных {len(A)*len(B)}")
print(f"  взаимная информация {MI:.4f} бит\n")
pos=sorted([x for x in MC if x[3]>x[4]], reverse=True)
neg=sorted([x for x in MC if x[3]<x[4]], reverse=True)
cum=0; k=0
for x in sorted(MC, reverse=True):
    cum+=x[0]; k+=1
    if cum>=0.8*MI: break
print(f"  80 % всей информации несут {k} сочетаний из {len(J)} ({k/len(J):.0%})")
# пустые клетки: ожидались, но не встретились
miss=[]
for a in A:
    for b in B:
        e=A[a]*B[b]/T
        if e>=8 and J.get((a,b),0)==0: miss.append((e,a,b))
miss.sort(reverse=True)
print(f"\n  АБСОЛЮТНЫЕ ЗАПРЕТЫ (ожидалось ≥8 случаев, встретилось 0): {len(miss)}")
for e,a,b in miss[:10]:
    print(f"     …{a} → {b}-   ожидалось {e:5.1f}, встретилось 0")
print(f"\n  САМЫЕ СИЛЬНЫЕ ПРИТЯЖЕНИЯ")
for m,a,b,n,e in pos[:6]:
    print(f"     …{a} → {b}-   {n:5d} против {e:6.1f} ожидаемых = {n/e:5.2f}×   ({m/MI:4.0%} всей информации)")
print(f"\n  САМЫЕ СИЛЬНЫЕ ОТТАЛКИВАНИЯ")
und=sorted([x for x in MC if x[3]<x[4] and x[4]>=20], key=lambda z:z[3]/z[4])
for m,a,b,n,e in und[:6]:
    print(f"     …{a} → {b}-   {n:5d} против {e:6.1f} ожидаемых = {n/e:5.2f}×   ({m/MI:4.0%})")
print("\n" + "="*104)
print("ТО ЖЕ ДЛЯ ЛАТЫНИ — сколько сочетаний нужно ей и есть ли у неё абсолютные запреты")
print("="*104)
ws=open("ref/latin.clean").read().split()
sizes=[len(l) for l in LN]; LL=[];i=0
for s in sizes:
    if i+s>len(ws): break
    LL.append(ws[i:i+s]); i+=s
J2,A2,B2=cells(LL); T2=sum(J2.values()); MC2=mi_cells(J2,A2,B2,T2); MI2=sum(x[0] for x in MC2)
cum=0;k2=0
for x in sorted(MC2, reverse=True):
    cum+=x[0]; k2+=1
    if cum>=0.8*MI2: break
miss2=[(A2[a]*B2[b]/T2,a,b) for a in A2 for b in B2 if A2[a]*B2[b]/T2>=8 and J2.get((a,b),0)==0]
print(f"  стыков {T2:,}, сочетаний {len(J2)} из {len(A2)*len(B2)}, MI {MI2:.4f} бит")
print(f"  80 % информации несут {k2} сочетаний ({k2/len(J2):.0%})")
print(f"  абсолютных запретов: {len(miss2)}")
print(f"\n  ИТОГ: Войнич — {k} сочетаний на 80 % и {len(miss)} запретов; латынь — {k2} и {len(miss2)}")
