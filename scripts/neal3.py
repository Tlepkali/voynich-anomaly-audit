# -*- coding: utf-8 -*-
import json, collections, random, statistics as st
D=json.load(open("parsed.json")); PG=D["pages"]
rows=[r for r in D["rows"] if r["locus"]=="P"]
TOP={"@","="}; SL="pf"
def clean(r): return [w for w in r["words"] if '?' not in w]
def has(w,gl=SL): return any(g in w for g in gl)
def perm_test(lines, gl=SL, B=5000):
    tails=[l[1:] for l in lines if len(l)>=3]
    obs=sum(1 for t in tails for i in range(len(t)-1) if has(t[i],gl) and has(t[i+1],gl))
    rnd=random.Random(17); null=[]
    flags=[[has(w,gl) for w in t] for t in tails]
    for _ in range(B):
        c=0
        for fl in flags:
            p=fl[:]; rnd.shuffle(p)
            c+=sum(1 for i in range(len(p)-1) if p[i] and p[i+1])
        null.append(c)
    null.sort(); m=st.mean(null); sd=st.stdev(null)
    ge=sum(1 for x in null if x>=obs)
    return obs, m, sd, (ge+1)/(B+1), null[int(.025*B)], null[int(.975*B)]
print("="*100); print("ЧЕСТНАЯ ПЕРЕСТАНОВКА ВНУТРИ СТРОКИ (5000 повторов, метки p/f тасуются в пределах своей строки)"); print("="*100)
print(f"  {'выборка':>34s} {'набл.':>6s} {'ожид.':>7s} {'±sd':>6s} {'отн.':>6s} {'95 % ожид.':>13s} {'p':>7s}")
def run(lab, sel, gl=SL):
    ls=[clean(r) for r in rows if sel(r)]
    o,m,sd,p,lo,hi=perm_test(ls,gl)
    print(f"  {lab:>34s} {o:6d} {m:7.1f} {sd:6.1f} {o/max(m,.01):5.2f}× [{lo:4d}; {hi:4d}] {p:7.3f}")
run("верхние строки абзацев (все)", lambda r: r["pos"] in TOP)
run("  то же, только раздел «звёзды»", lambda r: r["pos"] in TOP and PG.get(r["page"],{}).get("I")=="S")
run("  то же, только язык B", lambda r: r["pos"] in TOP and PG.get(r["page"],{}).get("L")=="B")
run("  то же, только травник", lambda r: r["pos"] in TOP and PG.get(r["page"],{}).get("I")=="H")
run("строки-продолжения", lambda r: r["pos"]=="+")
run("верхние строки, контроль t/k", lambda r: r["pos"] in TOP, "tk")
print("\n"+"="*100); print("ГДЕ НА СТРОКЕ СИДЯТ ОДНОНОГИЕ (утверждение: «около 2/3 поперёк верхней строки»)"); print("="*100)
ls=[clean(r) for r in rows if r["pos"] in TOP]
buck=[[0,0] for _ in range(6)]
for l in ls:
    n=len(l)
    if n<4: continue
    for i,w in enumerate(l):
        k=min(int(i/(n-1)*6),5); buck[k][1]+=1
        if has(w): buck[k][0]+=1
print("  доля слов с p/f по шестым долям верхней строки (включая 1-е слово):")
for i,(a,b) in enumerate(buck):
    bar="█"*int(a/max(b,1)*60)
    print(f"    {i/6:.2f}–{(i+1)/6:.2f}  {a:4d}/{b:4d} = {a/max(b,1):5.1%}  {bar}")
pos=[]
for l in ls:
    n=len(l)
    if n<4: continue
    for i,w in enumerate(l):
        if has(w) and i>0: pos.append(i/(n-1))
print(f"\n  медиана относительной позиции p/f-слов (без 1-го слова): {st.median(pos):.3f}  (n={len(pos)})")
print(f"  доля их в последней трети строки: {sum(1 for x in pos if x>=2/3)/len(pos):.1%} при равномерном ожидании ~33 %")
