# -*- coding: utf-8 -*-
"""Остаток начала строки: значим ли он и чем именно слово начала строки другое.
Нулевая модель: перемешивание слов ВНУТРИ СТРАНИЦЫ с сохранением длин строк —
состав страницы цел, разрушена только позиция в строке."""
import json, collections, statistics as st, random

def load(code="ZL3b-n"):
    D=json.load(open(f"data/parsed_{code}.json"))
    R=[r for r in D["rows"] if r["locus"]=="P"]
    for r in R: r["w"]=[w for w in r["words"] if "?" not in w]
    return [r for r in R if len(r["w"])>=3]

def tv(c1,c2):
    a=sum(c1.values()); b=sum(c2.values())
    return sum(abs(c1[c]/a-c2[c]/b) for c in set(c1)|set(c2))/2

def stat(rows, VT):
    """расхождение ОСТАТКОВ начальных слов и ОСТАТКОВ серединных"""
    FI=[r["w"][0] for r in rows if r["pos"]=="+"]
    MID=[w for r in rows for w in r["w"][1:]]
    a=collections.Counter(w[1] for w in FI if len(w)>2 and w[1:] in VT)
    b=collections.Counter(w[1] for w in MID if len(w)>2 and w[1:] in VT)
    return tv(a,b) if sum(a.values())>100 else float("nan")

R=load(); VT={w for r in R for w in r["w"]}
obs=stat(R,VT)
print("="*96); print("ЗНАЧИМОСТЬ ОСТАТКА"); print("="*96)
print(f"  наблюдённое расхождение остатков: {obs:.3f}")
by_page=collections.defaultdict(list)
for i,r in enumerate(R): by_page[r["page"]].append(i)
null=[]
for s in range(200):
    rnd=random.Random(1000+s); shuf=[dict(r) for r in R]
    for pg,idx in by_page.items():
        pool=[w for i in idx for w in R[i]["w"]]; rnd.shuffle(pool); k=0
        for i in idx:
            n=len(R[i]["w"]); shuf[i]["w"]=pool[k:k+n]; k+=n
    null.append(stat(shuf,VT))
null=[x for x in null if x==x]
ge=sum(1 for x in null if x>=obs)
print(f"  перемешивание внутри страницы (200 раз): {st.mean(null):.3f} [{min(null):.3f}; {max(null):.3f}]")
print(f"  p = {(ge+1)/(len(null)+1):.4f}   ({ge} из {len(null)} не ниже наблюдённого)")

print("\n"+"="*96); print("ЧЕМ ОСТАТОК НАЧАЛЬНОГО СЛОВА ОТЛИЧАЕТСЯ ОТ ОСТАТКА СЕРЕДИННОГО"); print("="*96)
FI=[r["w"][0] for r in R if r["pos"]=="+"]
MID=[w for r in R for w in r["w"][1:]]
cnt=collections.Counter(w for r in R for w in r["w"])
sf=[w[1:] for w in FI if len(w)>2 and w[1:] in VT]
sm=[w[1:] for w in MID if len(w)>2 and w[1:] in VT]
print(f"  {'':>22s} {'начало':>10s} {'середина':>10s}")
print(f"  {'остатков':>22s} {len(sf):10d} {len(sm):10d}")
print(f"  {'длина остатка':>22s} {st.mean(len(w) for w in sf):10.2f} {st.mean(len(w) for w in sm):10.2f}")
print(f"  {'медианная частота':>22s} {st.median(cnt[w] for w in sf):10.0f} {st.median(cnt[w] for w in sm):10.0f}")
print(f"  {'разных остатков':>22s} {len(set(sf)):10d} {len(set(sm)):10d}")
a=collections.Counter(w[0] for w in sf); b=collections.Counter(w[0] for w in sm)
ta,tb=sum(a.values()),sum(b.values())
print(f"\n  первый знак остатка, где разница больше двух пунктов:")
print(f"  {'знак':>6s} {'начало':>9s} {'середина':>10s} {'разница':>9s}")
for c in sorted(set(a)|set(b), key=lambda c: -abs(a[c]/ta-b[c]/tb)):
    d=a[c]/ta-b[c]/tb
    if abs(d)<0.02: break
    print(f"  {c:>6s} {a[c]/ta:9.1%} {b[c]/tb:10.1%} {d:+9.1%}")
print(f"\n  самые частые остатки НАЧАЛА : " + ", ".join(f"{w}·{n}" for w,n in collections.Counter(sf).most_common(8)))
print(f"  самые частые остатки СЕРЕДИНЫ: " + ", ".join(f"{w}·{n}" for w,n in collections.Counter(sm).most_common(8)))
