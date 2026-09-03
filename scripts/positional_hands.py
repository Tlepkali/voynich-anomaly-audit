# -*- coding: utf-8 -*-
import json, collections, math
D=json.load(open("parsed.json")); P=D["pages"]
byhand=collections.defaultdict(list)
for r in D["rows"]:
    if r["locus"]=="P":
        ws=[w for w in r["words"] if '?' not in w]
        if len(ws)>=5: byhand[P.get(r["page"],{}).get("H","?")].append(ws)
ALL=[l for v in byhand.values() for l in v]
vocA=collections.Counter(w for l in ALL for w in l)
def frac(lines, pre, bases):
    """доля слитной формы по пятым долям строки"""
    b=[[0,0] for _ in range(5)]
    for l in lines:
        n=len(l)-1
        for i,w in enumerate(l):
            k=min(int((i/n if n else 0)*5),4)
            if w in bases: b[k][1]+=1
            elif w.startswith(pre) and w[len(pre):] in bases: b[k][0]+=1; b[k][1]+=1
    return b
def z_first_last(b):
    a0,n0=b[0]; a4,n4=b[4]
    if n0<25 or n4<25: return None,None,None
    p1,p2=a0/n0,a4/n4
    pp=(a0+a4)/(n0+n4)
    se=math.sqrt(max(1e-12,pp*(1-pp)*(1/n0+1/n4)))
    return p1,p2,(p1-p2)/se
print("="*100)
print("ПОЗИЦИОННОЕ НАПИСАНИЕ ПО ПОЧЕРКАМ")
print("="*100)
for pre in ("s","sh","ot"):
    bases={X for X,n in vocA.items() if n>=25 and vocA.get(pre+X,0)>=15}
    if len(bases)<4: continue
    print(f"\n  элемент «{pre}»  (основ: {len(bases)})")
    print(f"    {'рука':>6s} {'строк':>7s} {'1-я пятая':>10s} {'5-я пятая':>10s} {'разница':>9s} {'z':>7s}")
    rows=[]
    for h,lines in sorted(byhand.items()):
        if len(lines)<150: continue
        b=frac(lines,pre,bases)
        p1,p2,z=z_first_last(b)
        if z is None:
            print(f"    {h:>6s} {len(lines):7d}   данных мало"); continue
        rows.append((h,p1,p2,z,len(lines)))
        mark="  ←" if abs(z)>3 else ""
        print(f"    {h:>6s} {len(lines):7d} {p1:9.1%} {p2:9.1%} {p1-p2:+8.1%} {z:7.1f}{mark}")
    if len(rows)>=3:
        ds=[r[1]-r[2] for r in rows]
        print(f"    разброс между руками: от {min(ds):+.1%} до {max(ds):+.1%}")
