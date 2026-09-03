# -*- coding: utf-8 -*-
import json, collections, random, math, statistics as st
D=json.load(open("parsed.json"))
def words(loc): return [w for r in D["rows"] if r["locus"]==loc for w in r["words"] if '?' not in w]
P=words("P"); L=words("L"); C=words("C"); R=words("R")
aP=collections.Counter(c for w in P for c in w)
aL=collections.Counter(c for w in L for c in w)
print("="*94); print("АЛФАВИТЫ: те же ли знаки в подписях"); print("="*94)
print(f"  сплошной текст: {len(aP)} знаков; подписи: {len(aL)}")
onlyL=set(aL)-set(aP); onlyP=set(aP)-set(aL)
print(f"  только в подписях: {sorted(onlyL) or '—'}")
print(f"  только в тексте:   {sorted(onlyP) or '—'}")
bad=[w for w in L if any(c in onlyL for c in w)]
print(f"  слов с чужими знаками: {len(bad)} из {len(L)} — {bad[:6]}")
L2=[w for w in L if not any(c in onlyL for c in w)]
print(f"  чистых подписей: {len(L2)}")
print("\n" + "="*94); print("СРАВНЕНИЕ ПРИ РАВНОМ ОБЪЁМЕ (выборки из сплошного текста того же размера)"); print("="*94)
rnd=random.Random(7)
def stats(ws):
    c=collections.Counter(ws)
    return dict(n=len(ws), ttr=len(c)/len(ws), hap=sum(1 for v in c.values() if v==1)/len(c),
                ln=st.mean(len(w) for w in ws))
def sample_stats(src, n, R=200):
    out=collections.defaultdict(list)
    for _ in range(R):
        i=rnd.randrange(0, len(src)-n)
        s=stats(src[i:i+n])
        for k,v in s.items(): out[k].append(v)
    return {k:(st.mean(v), st.pstdev(v)) for k,v in out.items() if k!="n"}
sl=stats(L2); sp=sample_stats(P, len(L2))
print(f"  {'мера':>12s} {'подписи':>10s} {'текст, тот же объём':>22s} {'z':>7s}")
for k,lab in (("ttr","TTR"),("hap","хапаксы"),("ln","длина")):
    m,sd=sp[k]; z=(sl[k]-m)/max(sd,1e-9)
    mark="  ←" if abs(z)>3 else ""
    print(f"  {lab:>12s} {sl[k]:10.3f} {m:14.3f} ±{sd:.3f} {z:7.1f}{mark}")
print("\n" + "="*94); print("ЕСТЬ ЛИ СЛОВА ПОДПИСЕЙ В СПЛОШНОМ ТЕКСТЕ"); print("="*94)
vp=collections.Counter(P)
inp=sum(1 for w in L2 if w in vp)
print(f"  слов подписей, встречающихся в тексте: {inp} из {len(L2)} ({inp/len(L2):.0%})")
# контроль: а какая доля у случайной выборки текста той же длины и частотности?
ctrl=[]
for _ in range(200):
    i=rnd.randrange(0,len(P)-len(L2))
    s=P[i:i+len(L2)]
    rest=collections.Counter(P[:i]+P[i+len(L2):])
    ctrl.append(sum(1 for w in s if w in rest)/len(s))
print(f"  контроль (кусок текста против остального текста): {st.mean(ctrl):.0%} ±{st.pstdev(ctrl):.1%}")
print("\n" + "="*94); print("ПЕРВЫЙ ЗНАК"); print("="*94)
fL=collections.Counter(w[0] for w in L2); fP=collections.Counter(w[0] for w in P)
tl,tp=sum(fL.values()),sum(fP.values())
print(f"  {'знак':>5s} {'подписи':>9s} {'текст':>8s} {'отношение':>11s}")
for k,_ in fL.most_common(8):
    a,b=fL[k]/tl, fP.get(k,0)/tp
    print(f"  {k:>5s} {a:8.1%} {b:7.1%} {(a/b if b else 0):10.2f}×")
