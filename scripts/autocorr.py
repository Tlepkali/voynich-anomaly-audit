# -*- coding: utf-8 -*-
import json, collections, math, os, random
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=6]
def acf(lines, dmax=6):
    """автокорреляция длин слов внутри строки, лаги 1..dmax"""
    out=[]
    for d in range(1,dmax+1):
        xs=[];ys=[]
        for l in lines:
            L=[len(w) for w in l]
            for i in range(len(L)-d): xs.append(L[i]); ys.append(L[i+d])
        if len(xs)<50: out.append(float('nan')); continue
        mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
        num=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
        den=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
        out.append(num/den if den else 0.0)
    return out
def cut_like(words, lens):
    out=[];k=0
    for n in lens:
        if k+n>len(words): break
        out.append(words[k:k+n]); k+=n
    return out
LENS=[len(l) for l in VL]
print("="*100)
print("АВТОКОРРЕЛЯЦИЯ ДЛИН СЛОВ ВНУТРИ СТРОКИ  (лаг 1 = соседнее слово)")
print("="*100)
print(f"  {'корпус':>22s} " + " ".join(f"{'лаг '+str(d):>8s}" for d in range(1,7)))
rows=[("Войнич", VL)]
NB=[l.split() for l in open("../naibbe/encrypted/nathist_output_ciphertext.txt").read().split("\n")]
NB=[l for l in NB if len(l)>=3]
rows.append(("Naibbe (его строки)", [l for l in NB if len(l)>=6]))
rows.append(("Naibbe (нарезка как у ВМ)", cut_like([w for l in NB for w in l], LENS)))
for tag,lab in (("latin","латынь"),("english","английский"),("wiki_de","немецкий"),
                ("wiki_it","итальянский"),("wiki_el","греческий"),("wiki_fi","финский")):
    p=f"ref/{tag}.clean"
    if os.path.exists(p):
        rows.append((lab, cut_like(open(p).read().split(), LENS)))
for lab,L in rows:
    a=acf(L)
    mk="  ←" if lab=="Войнич" else ""
    print(f"  {lab:>22s} " + " ".join(f"{x:8.3f}" for x in a) + mk)
print("\n  положительная автокорреляция = длинные слова тянутся к длинным, короткие к коротким")
# по разделам
print("\n" + "="*100); print("ПО РАЗДЕЛАМ РУКОПИСИ"); print("="*100)
P=D["pages"]; sec=collections.defaultdict(list)
for r in D["rows"]:
    if r["locus"]=="P":
        ws=[w for w in r["words"] if '?' not in w]
        if len(ws)>=6: sec[P.get(r["page"],{}).get("I","?")].append(ws)
NAMES={"H":"травник","B":"«банный»","S":"звёзды","T":"текст","C":"космология","P":"аптечный","A":"астро"}
for k,v in sorted(sec.items(), key=lambda x:-len(x[1])):
    if len(v)<80: continue
    a=acf(v,3)
    print(f"  {NAMES.get(k,k):>12s} ({len(v):4d} строк): " + " ".join(f"лаг{i+1}={x:6.3f}" for i,x in enumerate(a)))
