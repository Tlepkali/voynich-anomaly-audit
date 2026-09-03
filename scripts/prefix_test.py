# -*- coding: utf-8 -*-
import json, collections, math, glob, re, os, random
GB="naibbe/figure_utils/gaskell_bowern_2022/data"
D=json.load(open("parsed.json"))
VOY=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VOY=[l for l in VOY if len(l)>=4]
def norm(path):
    t=open(path,encoding="utf-8",errors="ignore").read(); out=[]
    for l in t.split("\n"):
        l=re.sub(r"[^A-Za-zÀ-ÿ'’ ]"," ",l)
        ws=[w.strip("'’").lower() for w in l.split() if w.strip("'’")]
        if len(ws)>=4: out.append(ws)
    return out
def test(lines, lab, minn=25):
    """для каждой первой буквы: доля остатков в словаре, начало строки против прочих"""
    voc=collections.Counter(w for l in lines for w in l[1:])
    first=collections.defaultdict(list); other=collections.defaultdict(list)
    for l in lines:
        w=l[0]
        if len(w)>1: first[w[0]].append(w[1:] in voc)
        for w in l[1:]:
            if len(w)>1: other[w[0]].append(w[1:] in voc)
    rows=[]
    for k in first:
        a,b=first[k],other.get(k,[])
        if len(a)<minn or len(b)<minn: continue
        pa=sum(a)/len(a); pb=sum(b)/len(b)
        # z для разности долей
        p=(sum(a)+sum(b))/(len(a)+len(b))
        se=math.sqrt(max(1e-12,p*(1-p)*(1/len(a)+1/len(b))))
        rows.append((pa-pb, k, len(a), pa, pb, (pa-pb)/se))
    rows.sort(reverse=True)
    return rows, len(lines)
print("="*100)
print("ПРИСТАВКА В НАЧАЛЕ СТРОКИ: снимаем первую букву, смотрим попадание остатка в словарь")
print("="*100)
CORP=[("ВОЙНИЧ", VOY)]
G=[norm(f) for f in sorted(glob.glob(GB+"/gibberish_transcriptions/*.txt"))]
CORP.append(("бессмыслица (пул)", [l for s in G for l in s]))
T=GB+"/meaningful/texts"
for f in sorted(glob.glob(T+"/Conlangs*Literary*")):
    nm=os.path.basename(f).split(" - ")[1]
    ls=norm(f)
    if sum(len(l) for l in ls)>=8000: CORP.append(("· "+nm, ls))
for f in sorted(glob.glob(T+"/Historical*"))[:2]:
    nm=os.path.basename(f).split(" - ")[1]
    ls=norm(f)
    if sum(len(l) for l in ls)>=8000: CORP.append(("hist "+nm, ls))
for lab,LN in CORP:
    rows,n=test(LN,lab)
    if not rows:
        print(f"\n  {lab}: строк {n} — данных мало"); continue
    top=rows[0]
    print(f"\n  {lab}  ({n} строк, букв с достаточными данными: {len(rows)})")
    print(f"    {'буква':>7s} {'строк':>6s} {'в начале':>9s} {'в прочих':>9s} {'разница':>9s} {'z':>7s}")
    for d,k,na,pa,pb,z in rows[:3]:
        print(f"    {k:>7s} {na:6d} {pa:8.1%} {pb:8.1%} {d*100:+7.1f}пп {z:7.1f}")
    print(f"    самая слабая: {rows[-1][1]} {rows[-1][0]:+.1%}")
