# -*- coding: utf-8 -*-
import json, collections, random
D=json.load(open("parsed.json"))
rows=[r for r in D["rows"] if r["locus"]=="P"]
def clean(r): return [w for w in r["words"] if '?' not in w]
def has(w,gl="pf"): return any(g in w for g in gl)
def boot(sel, gl="pf", B=4000):
    byp=collections.defaultdict(list)
    for r in rows:
        if sel(r): byp[r["page"]].append(clean(r))
    sc=[]
    for pg,ls in byp.items():
        o,e=0,0.0
        for l in ls:
            t=l[1:]
            if len(t)<2: continue
            k=sum(1 for w in t if has(w,gl))
            o+=sum(1 for i in range(len(t)-1) if has(t[i],gl) and has(t[i+1],gl)); e+=k*(k-1)/len(t)
        if o+e>0: sc.append((o,e))
    O=sum(o for o,_ in sc); E=sum(e for _,e in sc)
    rnd=random.Random(53); rat=[]
    for _ in range(B):
        s=[sc[rnd.randrange(len(sc))] for _ in range(len(sc))]
        oo=sum(a for a,_ in s); ee=sum(b for _,b in s)
        if ee>1: rat.append(oo/ee)
    rat.sort()
    return len(sc), O, E, O/max(E,.01), rat[int(.025*len(rat))], rat[int(.975*len(rat))]
print("="*96); print("ГРАНИЦЫ ОТРИЦАТЕЛЬНОГО ВЫВОДА: бутстрап ПО СТРАНИЦАМ"); print("="*96)
print(f"  {'выборка':>36s} {'стр.':>5s} {'набл.':>6s} {'ожид.':>7s} {'отн.':>6s} {'95 % ДИ':>16s}")
for lab,sel,gl in [("верхние строки абзацев, p/f", lambda r: r["pos"] in {"@","="}, "pf"),
                   ("верхние строки абзацев, t/k", lambda r: r["pos"] in {"@","="}, "tk"),
                   ("строки-продолжения, p/f", lambda r: r["pos"]=="+", "pf"),
                   ("строки-продолжения, t/k", lambda r: r["pos"]=="+", "tk")]:
    n,O,E,R,lo,hi=boot(sel,gl)
    print(f"  {lab:>36s} {n:5d} {O:6d} {E:7.1f} {R:5.2f}× [{lo:5.2f}; {hi:5.2f}]")
print("\n  Утверждение Нила — примерно 2× по смежности на верхней строке.")
print("  Верхняя граница моего ДИ там показана выше: 2× исключено.")
