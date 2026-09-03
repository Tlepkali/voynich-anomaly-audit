import json, collections, math, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows, pages = D["rows"], D["pages"]
P=[r for r in rows if r["locus"]=="P"]
LINES=[]
for r in P:
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=3: LINES.append({"w":ws,"pos":r["pos"],"page":r["page"]})
ALL=[w for l in LINES for w in l["w"]]; VOC=collections.Counter(ALL)
FIRST=[l["w"][0] for l in LINES]; LAST=[l["w"][-1] for l in LINES]
MID=[w for l in LINES for w in l["w"][1:-1]]
GLY=sorted({g for w in ALL for g in metrics.merge(w)})
def wilson(k,n):
    p=k/n; z=1.96; d=1+z*z/n
    c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return c-h,c+h

print("="*72)
print("ТЕСТ 6. Знак m приписан к обычному слову?")
print("="*72)
for name, ws in (("конец строки",LAST),("середина",MID)):
    sel=[w for w in ws if w.endswith('m') and len(w)>2]
    k=sum(1 for w in sel if w[:-1] in VOC)
    lo,hi=wilson(k,len(sel))
    print(f"  {name:14s} слов на m: {len(sel):4d}   без m остаётся словом: {k/len(sel):5.1%}  [{lo:.1%},{hi:.1%}]")
# с чем m чередуется
print("\n  чем ЗАМЕНЯЕТСЯ m: для слов вида X+m смотрим, какие X+g есть в словаре")
alt=collections.Counter()
for w in [w for w in LAST if w.endswith('m') and len(w)>2]:
    stem=w[:-1]
    for g in GLY:
        if stem+g in VOC: alt[g]+=1
for g,n in alt.most_common(8): print(f"     {stem and g:4s} {n:5d}")

print("\n"+"="*72)
print("ТЕСТ 7. Похоже ли последнее слово строки на обрезанное?")
print("="*72)
print("  доля слов, к которым можно приписать один знак и получить слово из словаря\n")
for name, ws in (("конец строки",LAST),("середина",MID),("начало строки",FIRST)):
    sub=random.Random(5).sample(ws, min(2500,len(ws)))
    k=sum(1 for w in sub if any(w+g in VOC for g in GLY))
    lo,hi=wilson(k,len(sub))
    print(f"  {name:14s} n={len(sub):5d}   продолжается до слова: {k/len(sub):5.1%}  [{lo:.1%},{hi:.1%}]")

print("\n"+"="*72)
print("ТЕСТ 8. Зависит ли укорочение от того, длинная строка или короткая?")
print("="*72)
by=collections.defaultdict(lambda:[[],[]])
for l in LINES:
    n=len(l["w"]); b=min(3,max(0,(n-4)//3))
    by[b][0].append(len(l["w"][-1])); by[b][1].append(sum(len(w) for w in l["w"][1:-1])/max(1,len(l["w"])-2))
names={0:"4–6 слов",1:"7–9 слов",2:"10–12 слов",3:"13+ слов"}
for b in sorted(by):
    la,mi=by[b]
    print(f"  строка {names[b]:11s} n={len(la):5d}   последнее слово {sum(la)/len(la):.2f}   "
          f"середина {sum(mi)/len(mi):.2f}   разрыв {sum(mi)/len(mi)-sum(la)/len(la):+.2f}")

print("\n"+"="*72)
print("ТЕСТ 9. Первое слово строки — повтор чего-то из предыдущей строки?")
print("="*72)
hit=0; tot=0; ctrl=0
for i in range(1,len(LINES)):
    if LINES[i]["page"]!=LINES[i-1]["page"]: continue
    prev=set(LINES[i-1]["w"]); tot+=1
    if LINES[i]["w"][0] in prev: hit+=1
    if LINES[i]["w"][len(LINES[i]["w"])//2] in prev: ctrl+=1
print(f"  первое слово встречалось в предыдущей строке: {hit/tot:.1%}")
print(f"  контроль — слово из середины той же строки:    {ctrl/tot:.1%}")
