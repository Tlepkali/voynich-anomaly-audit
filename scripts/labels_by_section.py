# -*- coding: utf-8 -*-
import json, collections, math, statistics as st, random
D=json.load(open("parsed.json")); PG=D["pages"]
NAME={"H":"травник","B":"«банный»","S":"звёзды","T":"текст","C":"космология",
      "P":"аптечный","A":"астрономия","Z":"зодиак"}
lab=collections.defaultdict(list); txt=collections.defaultdict(list)
for r in D["rows"]:
    s=PG.get(r["page"],{}).get("I","?")
    ws=[w for w in r["words"] if '?' not in w]
    if r["locus"]=="L": lab[s]+=ws
    elif r["locus"]=="P": txt[s]+=ws
ALLP=[w for v in txt.values() for w in v]
vp=collections.Counter(ALLP)
def z2(a,na,b,nb):
    if na<8 or nb<8: return 0.0
    p=(a+b)/(na+nb); se=math.sqrt(max(1e-12,p*(1-p)*(1/na+1/nb)))
    return (a/na-b/nb)/se
print("="*106)
print("ПОДПИСИ ПО РАЗДЕЛАМ: сравнение с текстом ТОГО ЖЕ раздела")
print("="*106)
print(f"  {'раздел':>13s} {'подпис.':>7s} {'текста':>7s} | {'на o':>16s} | {'ot/ok':>16s} | {'есть в тексте':>15s} | {'длина':>12s}")
rows=[]
for s in sorted(lab, key=lambda k:-len(lab[k])):
    L=lab[s]; T=txt.get(s,[])
    if len(L)<25: continue
    def r(f,ws): return sum(1 for w in ws if f(w)), len(ws)
    o1,n1=r(lambda w:w.startswith("o"),L); o2,n2=r(lambda w:w.startswith("o"),T) if T else (0,0)
    k1,_=r(lambda w:w.startswith(("ot","ok")),L); k2,_=r(lambda w:w.startswith(("ot","ok")),T) if T else (0,0)
    i1=sum(1 for w in L if w in vp)/len(L)
    zo=z2(o1,n1,o2,n2) if n2 else 0
    zk=z2(k1,n1,k2,n2) if n2 else 0
    ml=st.mean(len(w) for w in L); mt=st.mean(len(w) for w in T) if T else 0
    rows.append((s,len(L),len(T),o1/n1,o2/n2 if n2 else 0,zo,k1/n1,k2/n2 if n2 else 0,zk,i1,ml,mt))
for s,nl,nt,a,b,zo,c,d,zk,i1,ml,mt in rows:
    mk="←" if zo>4 else " "
    print(f"  {NAME.get(s,s):>13s} {nl:7d} {nt:7d} | {a:6.0%} vs {b:5.0%} {zo:5.1f}{mk}| {c:6.0%} vs {d:5.0%} {zk:5.1f} | {i1:14.0%} | {ml:5.2f} vs {mt:4.2f}")
print("\n  «есть в тексте» — доля слов подписи, встречающихся в сплошном тексте всей рукописи")
print("\n" + "="*106); print("ОДНОРОДНЫ ЛИ ПОДПИСИ МЕЖДУ РАЗДЕЛАМИ"); print("="*106)
big=[(s,lab[s]) for s in lab if len(lab[s])>=60]
print(f"  {'раздел':>13s} {'на o':>7s} {'ot/ok':>7s} {'TTR':>7s} {'общий словарь':>14s}")
for s,L in sorted(big,key=lambda x:-len(x[1])):
    c=collections.Counter(L)
    print(f"  {NAME.get(s,s):>13s} {sum(1 for w in L if w[0]=='o')/len(L):6.0%} "
          f"{sum(1 for w in L if w.startswith(('ot','ok')))/len(L):6.0%} "
          f"{len(c)/len(L):7.3f} {sum(1 for w in L if w in vp)/len(L):13.0%}")
# разброс между разделами против внутреннего разброса
vals=[sum(1 for w in L if w[0]=='o')/len(L) for _,L in big]
print(f"\n  разброс доли «на o» между разделами: от {min(vals):.0%} до {max(vals):.0%}")
