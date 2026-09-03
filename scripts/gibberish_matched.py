# -*- coding: utf-8 -*-
import json, collections, math, random, glob, re, statistics as st
GB="naibbe/figure_utils/gaskell_bowern_2022/data"
D=json.load(open("parsed.json"))
VOY=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VOY=[l for l in VOY if len(l)>=2]
def load(path):
    t=open(path,encoding="utf-8",errors="ignore").read(); out=[]
    for l in t.split("\n"):
        l=re.sub(r"[^A-Za-zÀ-ÿ' ]"," ",l)
        ws=[w.strip("'").lower() for w in l.split() if w.strip("'")]
        if len(ws)>=2: out.append(ws)
    return out
GIB=[load(f) for f in sorted(glob.glob(GB+"/gibberish_transcriptions/*.txt"))]
GIB=[s for s in GIB if sum(len(l) for l in s)>=150]
def voc(words):
    c=collections.Counter(words)
    hap=sum(1 for v in c.values() if v==1)/len(c)
    fr=sorted(c.values(),reverse=True)[:400]
    if len(fr)<20: return None
    xs=[math.log(i+1) for i in range(len(fr))]; ys=[math.log(v) for v in fr]
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    z=sum((a-mx)*(b-my) for a,b in zip(xs,ys))/sum((a-mx)**2 for a in xs)
    return len(c)/len(words), hap, z
print("="*100)
print("СЛОВАРНЫЕ МЕРЫ ПРИ РАВНОМ ОБЪЁМЕ: каждый образец бессмыслицы против куска рукописи той же длины")
print("="*100)
rnd=random.Random(5)
VF=[w for l in VOY for w in l]
rowsG=[];rowsV=[]
for s in GIB:
    ws=[w for l in s for w in l]; n=len(ws)
    g=voc(ws)
    i=rnd.randrange(0,len(VF)-n)
    v=voc(VF[i:i+n])
    if g and v: rowsG.append(g); rowsV.append(v)
print(f"  образцов сравнено: {len(rowsG)}, медианный объём {int(st.median([sum(len(l) for l in s) for s in GIB]))} слов\n")
print(f"  {'мера':>12s} {'бессмыслица':>26s} {'Войнич (тот же объём)':>26s}")
for k,lab in ((0,"TTR"),(1,"хапаксы"),(2,"наклон Ципфа")):
    a=[r[k] for r in rowsG]; b=[r[k] for r in rowsV]
    print(f"  {lab:>12s} {st.mean(a):11.3f} ± {st.pstdev(a):.3f}      {st.mean(b):11.3f} ± {st.pstdev(b):.3f}")
# сцепление длин и соседство ПО ОБРАЗЦАМ, с разбросом
def acf1(s):
    xs=[];ys=[]
    for l in s:
        L=[len(w) for w in l]
        for i in range(len(L)-1): xs.append(L[i]); ys.append(L[i+1])
    if len(xs)<40: return None
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    num=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
    den=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    return num/den if den else None
ga=[x for x in (acf1(s) for s in GIB) if x is not None]
# Войнич по страницам сопоставимого объёма
pg=collections.defaultdict(list)
for r in D["rows"]:
    if r["locus"]=="P":
        ws=[w for w in r["words"] if '?' not in w]
        if len(ws)>=2: pg[r["page"]].append(ws)
va=[x for x in (acf1(v) for v in pg.values() if sum(len(l) for l in v)>=150) if x is not None]
print(f"\n  сцепление длин по образцам:")
print(f"    бессмыслица: медиана {st.median(ga):+.3f}, положительных {sum(1 for x in ga if x>0)}/{len(ga)}")
print(f"    Войнич по страницам: медиана {st.median(va):+.3f}, положительных {sum(1 for x in va if x>0)}/{len(va)}")
