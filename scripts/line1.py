import json, collections, math
D=json.load(open("parsed.json")); rows, pages = D["rows"], D["pages"]
# только текст абзацев: у подписей и круговых надписей строки нет
P=[r for r in rows if r["locus"]=="P"]
LINES=[]
for r in P:
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=3: LINES.append({"w":ws,"pos":r["pos"],"page":r["page"]})
ALL=[w for l in LINES for w in l["w"]]
print(f"строк абзацного текста: {len(LINES)}, слов: {len(ALL)}\n")

print("="*70); print("ДЛИНА СЛОВА ПО МЕСТУ В СТРОКЕ"); print("="*70)
buck=collections.defaultdict(list)
for l in LINES:
    n=len(l["w"])
    for i,w in enumerate(l["w"]):
        key = "1-е" if i==0 else ("2-е" if i==1 else ("последнее" if i==n-1 else ("предпосл." if i==n-2 else "середина")))
        buck[key].append(len(w))
for k in ["1-е","2-е","середина","предпосл.","последнее"]:
    v=buck[k]; mu=sum(v)/len(v)
    sd=(sum((x-mu)**2 for x in v)/len(v))**0.5
    print(f"  {k:11s} n={len(v):6d}  средняя длина {mu:5.2f}  ст.откл {sd:4.2f}  {'█'*int((mu-4)*14)}")

print("\n"+"="*70); print("ПЕРВАЯ БУКВА СЛОВА — по месту в строке"); print("="*70)
def fd(ws):
    c=collections.Counter(w[0] for w in ws); T=sum(c.values()); return c,T
groups={"1-е слово":[l["w"][0] for l in LINES],
        "2-е слово":[l["w"][1] for l in LINES],
        "середина":[w for l in LINES for w in l["w"][2:-1]],
        "последнее":[l["w"][-1] for l in LINES]}
keys=sorted({w[0] for ws in groups.values() for w in ws},
            key=lambda c:-sum(1 for w in groups["середина"] if w[0]==c))
print(f"  {'буква':6s}" + "".join(f"{g[:10]:>12s}" for g in groups))
for c in keys[:12]:
    row=f"  {c:6s}"
    for g,ws in groups.items():
        cc,T=fd(ws); row+=f"{cc.get(c,0)/T:11.1%} "
    print(row)

print("\n"+"="*70); print("ПОСЛЕДНЯЯ БУКВА СЛОВА — по месту в строке"); print("="*70)
def ld(ws):
    c=collections.Counter(w[-1] for w in ws); T=sum(c.values()); return c,T
keys2=sorted({w[-1] for ws in groups.values() for w in ws},
             key=lambda c:-sum(1 for w in groups["середина"] if w[-1]==c))
print(f"  {'буква':6s}" + "".join(f"{g[:10]:>12s}" for g in groups))
for c in keys2[:10]:
    row=f"  {c:6s}"
    for g,ws in groups.items():
        cc,T=ld(ws); row+=f"{cc.get(c,0)/T:11.1%} "
    print(row)

print("\n"+"="*70)
print("РЕШАЮЩИЙ ТЕСТ: это украшенные заглавные или свойство КАЖДОЙ строки?")
print("="*70)
first_par=[l for l in LINES if l["pos"] in "@*"]      # первая строка абзаца
cont    =[l for l in LINES if l["pos"]=="+"]          # строка-продолжение
mid=[w for l in LINES for w in l["w"][2:-1]]
cm,Tm=fd(mid)
for name, ls in (("первая строка абзаца",first_par),("строка-продолжение",cont)):
    ws=[l["w"][0] for l in ls]; cc,T=fd(ws)
    parts=[]
    for c in "pfktdsy":
        r=(cc.get(c,0)/T)/max(cm.get(c,0)/Tm,1e-9)
        parts.append(f"{c} ×{r:5.1f}")
    print(f"  {name:22s} (n={T:5d})  " + "  ".join(parts))
