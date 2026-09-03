# -*- coding: utf-8 -*-
import json, collections, math, statistics as st
D=json.load(open("parsed.json")); PG=D["pages"]
def lab(sec=None):
    out=[]
    for r in D["rows"]:
        if r["locus"]=="L":
            s=PG.get(r["page"],{}).get("I","?")
            if sec is None or (s==sec if isinstance(sec,str) else s in sec):
                out += [w for w in r["words"] if '?' not in w]
    return out
Z=lab("Z"); OTH=[w for w in lab() if w not in ()]
OTHER=[]
for r in D["rows"]:
    if r["locus"]=="L" and PG.get(r["page"],{}).get("I","?")!="Z":
        OTHER += [w for w in r["words"] if '?' not in w]
P=[w for r in D["rows"] if r["locus"]=="P" for w in r["words"] if '?' not in w]
def z2(a,na,b,nb):
    if na<10 or nb<10: return 0
    p=(a+b)/(na+nb); se=math.sqrt(max(1e-12,p*(1-p)*(1/na+1/nb)))
    return (a/na-b/nb)/se
print("="*100)
print(f"ЗОДИАКАЛЬНЫЕ ПОДПИСИ: {len(Z)} слов, 12 страниц. Контроли — прочие подписи ({len(OTHER)}) и текст ({len(P):,})")
print("="*100)
TESTS=[("начинается на ot",lambda w:w.startswith("ot")),
       ("начинается на ok",lambda w:w.startswith("ok")),
       ("начинается на ot или ok",lambda w:w.startswith("ot") or w.startswith("ok")),
       ("начинается на o",lambda w:w.startswith("o")),
       ("начинается на yk",lambda w:w.startswith("yk")),
       ("начинается на qo",lambda w:w.startswith("qo")),
       ("кончается на y",lambda w:w.endswith("y")),
       ("кончается на l",lambda w:w.endswith("l")),
       ("кончается на r",lambda w:w.endswith("r"))]
print(f"  {'признак':>26s} {'зодиак':>8s} {'проч. подписи':>14s} {'z':>6s} | {'текст':>7s} {'z':>6s}")
for name,f in TESTS:
    a=sum(1 for w in Z if f(w)); b=sum(1 for w in OTHER if f(w)); c=sum(1 for w in P if f(w))
    zz1=z2(a,len(Z),b,len(OTHER)); zz2=z2(a,len(Z),c,len(P))
    m1="←" if abs(zz1)>3 else " "
    m2="←" if abs(zz2)>3 else " "
    print(f"  {name:>26s} {a/len(Z):7.1%} {b/len(OTHER):13.1%} {zz1:6.1f}{m1}| {c/len(P):6.1%} {zz2:6.1f}{m2}")
print("\n" + "="*100); print("ДЛИНА: правда ли зодиакальные подписи короткие"); print("="*100)
for name,ws in (("зодиакальные",Z),("прочие подписи",OTHER),("сплошной текст",P)):
    L=[len(w) for w in ws]
    print(f"  {name:>18s}: средняя {st.mean(L):.2f}, медиана {sorted(L)[len(L)//2]}, СКО {st.pstdev(L):.2f}")
print("\n" + "="*100); print("СОСТАВ: что это за слова"); print("="*100)
c=collections.Counter(Z)
print(f"  разных слов {len(c)} из {len(Z)} (TTR {len(c)/len(Z):.3f})")
print("  самые частые: " + ", ".join(f"{w}({n})" for w,n in c.most_common(10)))
vp=collections.Counter(P)
print(f"  встречаются в сплошном тексте: {sum(1 for w in Z if w in vp)/len(Z):.0%}")
print(f"  «парная» структура ot-ol-al: слов вида ot+X, где X есть в подписях: ", end="")
cz=set(Z)|set(OTHER)
print(sum(1 for w in Z if w.startswith("ot") and w[2:] in cz))
