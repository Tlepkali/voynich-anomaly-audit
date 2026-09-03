# -*- coding: utf-8 -*-
import json, collections, random, statistics as st
D=json.load(open("parsed.json")); PG=D["pages"]
NAME={"H":"травник","B":"«банный»","S":"звёзды","T":"текст","P":"аптечный"}
sec=collections.defaultdict(list)
for r in D["rows"]:
    if r["locus"]!="P": continue
    m=PG.get(r["page"],{}); ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=2: sec[(m.get("I","?"),m.get("L","?"))].append((r["page"],ws))
def pool(s,L=None): return [x for (a,b),v in sec.items() if a==s and (L is None or b==L) for x in v]
print("="*96); print("НЕ ДЕРЖИТСЯ ЛИ TTR «БАННОГО» НА НЕСКОЛЬКИХ СТРАНИЦАХ (постранично, ≥250 слов)"); print("="*96)
print(f"  {'раздел':>10s} {'страниц':>8s} {'TTR@250 медиана':>16s} {'разброс':>18s} {'мин страница':>16s}")
for s in ["B","S","H"]:
    ls=pool(s,"B"); byp=collections.defaultdict(list)
    for p,l in ls: byp[p]+=l
    vals=[]
    for p,f in byp.items():
        if len(f)<250: continue
        rnd=random.Random(9); v=[]
        for _ in range(10):
            i=rnd.randrange(0,len(f)-249); v.append(len(set(f[i:i+250]))/250)
        vals.append((st.mean(v),p))
    if not vals: continue
    vals.sort(); xs=[x for x,_ in vals]
    print(f"  {NAME[s]:>10s} {len(vals):8d} {st.median(xs):16.3f}   [{xs[0]:.3f}; {xs[-1]:.3f}]   {vals[0][1]:>12s} {xs[0]:.3f}")
print("\n"+"="*96); print("ПОВТОР СЛОВА В ПРЕДЕЛАХ ОКНА 10 СЛОВ (против перемешивания внутри раздела)"); print("="*96)
print(f"  {'раздел':>10s} {'наблюдено':>10s} {'случайно':>9s} {'отношение':>10s}")
for s in ["B","S","H","P","T"]:
    L=pool(s); f=[w for _,l in L for w in l]
    def cnt(seq):
        n=0
        for i in range(len(seq)):
            if seq[i] in seq[i+1:i+11]: n+=1
        return n
    o=cnt(f); rnd=random.Random(4); acc=0
    for _ in range(6):
        g=f[:]; rnd.shuffle(g); acc+=cnt(g)/6
    print(f"  {NAME[s]:>10s} {o/len(f):9.1%} {acc/len(f):8.1%} {o/max(acc,1):9.2f}×")
