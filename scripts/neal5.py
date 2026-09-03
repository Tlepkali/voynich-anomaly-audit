# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, math
D=json.load(open("parsed.json")); PG=D["pages"]
rows=[r for r in D["rows"] if r["locus"]=="P"]
def clean(r): return [w for w in r["words"] if '?' not in w]
def has(w,gl="pf"): return any(g in w for g in gl)
def binom_two_sided(k,n):
    def c(a,b): return math.comb(a,b)
    tot=2**n; pk=c(n,k)
    s=sum(c(n,i) for i in range(n+1) if c(n,i)<=pk)
    return min(1.0, s/tot)
byp=collections.defaultdict(list)
for r in rows:
    if r["pos"]=="+": byp[r["page"]].append(clean(r))
def page_stat(lines):
    tails=[l[1:] for l in lines if len(l)>=3]
    o=sum(1 for t in tails for i in range(len(t)-1) if has(t[i]) and has(t[i+1]))
    e=sum((lambda k,n: k*(k-1)/n)(sum(1 for w in t if has(w)),len(t)) for t in tails if len(t)>0)
    return o,e
sc=[(page_stat(v)[0],page_stat(v)[1],pg) for pg,v in byp.items()]
sc=[x for x in sc if x[0]+x[1]>0]
pos=sum(1 for o,e,_ in sc if o>e); neg=sum(1 for o,e,_ in sc if o<e)
print("="*94); print("СТРОКИ-ПРОДОЛЖЕНИЯ: устойчивость эффекта 1,30× по страницам"); print("="*94)
print(f"  страниц с вкладом: {len(sc)};  выше ожидания {pos}, ниже {neg}, поровну {len(sc)-pos-neg}")
print(f"  знаковый тест (биномиальный, двусторонний): p = {binom_two_sided(pos,pos+neg):.4f}")
rnd=random.Random(31); B=4000; rat=[]
for _ in range(B):
    s=[sc[rnd.randrange(len(sc))] for _ in range(len(sc))]
    O=sum(o for o,_,_ in s); E=sum(e for _,e,_ in s)
    if E>1: rat.append(O/E)
rat.sort()
print(f"  бутстрап ПО СТРАНИЦАМ (4000): отношение {sum(o for o,_,_ in sc)/sum(e for _,e,_ in sc):.2f}×, 95 % ДИ [{rat[int(.025*B)]:.2f}; {rat[int(.975*B)]:.2f}]")
print(f"  доля превышения от пяти главных страниц: {sum(sorted([o-e for o,e,_ in sc],reverse=True)[:5])/max(sum(o for o,_,_ in sc)-sum(e for _,e,_ in sc),.01):.0%} из {len(sc)} страниц")
print("\n"+"="*94); print("СТРОГАЯ СМЕЖНОСТЬ ИЛИ ОКНО: на каком расстоянии сидят одноногие"); print("="*94)
lines=[clean(r) for r in rows if r["pos"]=="+"]
tails=[l[1:] for l in lines if len(l)>=3]
F=[[has(w) for w in t] for t in tails]
def at(d, flags):
    return sum(1 for fl in flags for i in range(len(fl)-d) if fl[i] and fl[i+d])
rnd=random.Random(41)
print(f"  {'расстояние':>11s} {'набл.':>6s} {'ожид.':>7s} {'отн.':>6s}")
for d in [1,2,3,4]:
    o=at(d,F); null=[]
    for _ in range(1500):
        P=[]
        for fl in F:
            p=fl[:]; rnd.shuffle(p); P.append(p)
        null.append(at(d,P))
    m=st.mean(null)
    print(f"  {d:>11d} {o:6d} {m:7.1f} {o/max(m,.01):5.2f}×")
print("\n"+"="*94); print("НЕ ВТОРАЯ ЛИ ЭТО СТРОКА АБЗАЦА (квазиверхняя)"); print("="*94)
seq=collections.defaultdict(list); cur=None; idx=0
for r in rows:
    if r["pos"] in {"@","="}: cur=(r["page"],r["line"]); idx=0
    elif r["pos"]=="+" and cur: idx+=1; seq[min(idx,4)].append(clean(r))
print(f"  {'строка абзаца':>16s} {'строк':>6s} {'доля p/f':>9s} {'набл.':>6s} {'ожид.':>7s} {'отн.':>6s}")
for k in sorted(seq):
    ls=seq[k]; f=[w for l in ls for w in l]
    o,e=0,0.0
    for l in ls:
        t=l[1:]
        if len(t)<2: continue
        kk=sum(1 for w in t if has(w))
        o+=sum(1 for i in range(len(t)-1) if has(t[i]) and has(t[i+1])); e+=kk*(kk-1)/len(t)
    lab=f"{k}-я" if k<4 else "5-я и дальше"
    print(f"  {lab:>16s} {len(ls):6d} {sum(1 for w in f if has(w))/len(f):8.1%} {o:6d} {e:7.1f} {o/max(e,.01):5.2f}×")
