# -*- coding: utf-8 -*-
"""РЕШАЮЩИЙ КОНТРОЛЬ к остатку начала строки.

Прошлое сравнение нечисто: у начальных слов снимается один набор знаков
(d, q, y, o, s, t, p), у серединных — другой (o, c, q, s), а распределение
остатка от снятого знака ЗАВИСИТ (после q почти всегда o). Разница могла
целиком идти от разного состава снятых знаков.

Здесь сравнение СТРАТИФИЦИРОВАНО: для каждого снятого знака c остатки
начальных слов сравниваются с остатками СЕРЕДИННЫХ слов, начинающихся на
ТОТ ЖЕ знак c. Общая величина — среднее по стратам, взвешенное числом
начальных слов. Если она падает к нулю, находка снимается.
"""
import json, collections, statistics as st, random

def load(code="ZL3b-n"):
    D=json.load(open(f"data/parsed_{code}.json"))
    R=[r for r in D["rows"] if r["locus"]=="P"]
    for r in R: r["w"]=[w for w in r["words"] if "?" not in w]
    return [r for r in R if len(r["w"])>=3]

def tv(c1,c2):
    a=sum(c1.values()); b=sum(c2.values())
    if not a or not b: return float("nan")
    return sum(abs(c1[c]/a-c2[c]/b) for c in set(c1)|set(c2))/2

def strat(rows, VT, minn=40, detail=False):
    FI=[r["w"][0] for r in rows if r["pos"]=="+"]
    MID=[w for r in rows for w in r["w"][1:]]
    dec_f=collections.defaultdict(collections.Counter)   # снятый знак -> первый знак остатка
    dec_m=collections.defaultdict(collections.Counter)
    for w in FI:
        if len(w)>2 and w[1:] in VT: dec_f[w[0]][w[1]]+=1
    for w in MID:
        if len(w)>2 and w[1:] in VT: dec_m[w[0]][w[1]]+=1
    tot=0; acc=0.0; lines=[]
    for c in sorted(dec_f, key=lambda c:-sum(dec_f[c].values())):
        nf=sum(dec_f[c].values()); nm=sum(dec_m[c].values())
        if nf<minn or nm<minn: continue
        d=tv(dec_f[c],dec_m[c]); acc+=d*nf; tot+=nf
        lines.append((c,nf,nm,d))
    if detail: return acc/tot if tot else float("nan"), lines
    return acc/tot if tot else float("nan")

R=load(); VT={w for r in R for w in r["w"]}
obs,lines=strat(R,VT,detail=True)
print("="*96); print("СТРАТИФИЦИРОВАННОЕ СРАВНЕНИЕ ОСТАТКОВ (ZL3b)"); print("="*96)
print(f"  {'снятый знак':>12s} {'начал.':>7s} {'серед.':>7s} {'расхождение остатков':>21s}")
for c,nf,nm,d in lines:
    print(f"  {c:>12s} {nf:7d} {nm:7d} {d:21.3f}")
print(f"\n  ВЗВЕШЕННОЕ СРЕДНЕЕ ПО СТРАТАМ: {obs:.3f}")
print(f"  (нестратифицированное было 0,262 — разница показывает вклад состава снятых знаков)")

null=[]
by_page=collections.defaultdict(list)
for i,r in enumerate(R): by_page[r["page"]].append(i)
for s in range(200):
    rnd=random.Random(2000+s); shuf=[dict(r) for r in R]
    for pg,idx in by_page.items():
        pool=[w for i in idx for w in R[i]["w"]]; rnd.shuffle(pool); k=0
        for i in idx:
            n=len(R[i]["w"]); shuf[i]["w"]=pool[k:k+n]; k+=n
    x=strat(shuf,VT)
    if x==x: null.append(x)
ge=sum(1 for x in null if x>=obs)
print(f"\n  нуль (перемешивание внутри страницы, {len(null)} раз): {st.mean(null):.3f} [{min(null):.3f}; {max(null):.3f}]")
print(f"  p = {(ge+1)/(len(null)+1):.4f}")

print("\n"+"="*96); print("ТО ЖЕ НА ШЕСТИ ТРАНСКРИПЦИЯХ"); print("="*96)
print(f"  {'транскрипция':>22s} {'нестратиф.':>11s} {'СТРАТИФИЦ.':>11s} {'нуль':>8s}")
for code,lab in [("ZL3b-n","EVA Зандб.–Ландини"),("IT2a-n","EVA Такахаси"),("RF1b-e","EVA Reference"),
                 ("GC2a-n","v101 Класton"),("FG2a-n","FSG"),("CD2a-n","Карриер")]:
    try:
        Rx=load(code); VTx={w for r in Rx for w in r["w"]}
        FI=[r["w"][0] for r in Rx if r["pos"]=="+"]; MID=[w for r in Rx for w in r["w"][1:]]
        a=collections.Counter(w[1] for w in FI if len(w)>2 and w[1:] in VTx)
        b=collections.Counter(w[1] for w in MID if len(w)>2 and w[1:] in VTx)
        ns=tv(a,b); sx=strat(Rx,VTx)
        by=collections.defaultdict(list)
        for i,r in enumerate(Rx): by[r["page"]].append(i)
        nl=[]
        for s in range(30):
            rnd=random.Random(3000+s); sh=[dict(r) for r in Rx]
            for pg,idx in by.items():
                pool=[w for i in idx for w in Rx[i]["w"]]; rnd.shuffle(pool); k=0
                for i in idx:
                    n=len(Rx[i]["w"]); sh[i]["w"]=pool[k:k+n]; k+=n
            y=strat(sh,VTx)
            if y==y: nl.append(y)
        print(f"  {lab:>22s} {ns:11.3f} {sx:11.3f} {st.mean(nl):8.3f}")
    except Exception as e:
        print(f"  {lab:>22s} — {e}")
