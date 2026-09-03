# -*- coding: utf-8 -*-
import json, collections, math, random
D=json.load(open("parsed.json"))
VOY=[w for r in D["rows"] if r["locus"]=="P" for w in r["words"] if '?' not in w]
freq=collections.Counter(VOY)
ALL=[w for w,n in freq.items() if n>=2]
CAND=[w for w,_ in freq.most_common(500)]
def lev(a,b):
    if a==b: return 0
    if len(a)>len(b): a,b=b,a
    prev=list(range(len(a)+1))
    for j,cb in enumerate(b,1):
        cur=[j]
        for i,ca in enumerate(a,1):
            cur.append(min(prev[i]+1, cur[i-1]+1, prev[i-1]+(ca!=cb)))
        prev=cur
    return prev[-1]
M={c:{t:lev(c,t) for t in ALL} for c in CAND}
def mk(types):
    LF=[math.log(freq[w]) for w in types]; LN=[len(w) for w in types]
    def corr(x,y):
        n=len(x); mx=sum(x)/n; my=sum(y)/n
        c=sum((a-mx)*(b-my) for a,b in zip(x,y))
        d=math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
        return c/d if d else 0.0
    rlf=corr(LN,LF)
    def partial(cs):
        dm=[min(M[c][t] for c in cs) for t in types]
        a=corr(dm,LF); b=corr(dm,LN)
        return (a-b*rlf)/math.sqrt(max(1e-12,(1-b*b)*(1-rlf*rlf)))
    return partial
rnd=random.Random(11)
sh=ALL[:]; rnd.shuffle(sh)
A,B=sh[:len(sh)//2], sh[len(sh)//2:]
pA,pB=mk(A),mk(B)
BASE=["daiin","ol","chedy"]
print("="*94); print("ПРОВЕРКА НА ОТЛОЖЕННОЙ ПОЛОВИНЕ СЛОВАРЯ"); print("="*94)
print(f"  словарь разбит пополам: {len(A)} и {len(B)} типов\n")
print(f"  {'набор центров':>34s} {'выбран на A':>12s} {'проверен на B':>14s}")
print(f"  {'тройка Тимма':>34s} {pA(BASE):12.4f} {pB(BASE):14.4f}")
# четвёртый выбирается ТОЛЬКО на A
best=sorted(((pA(BASE+[c]), c) for c in CAND if c not in BASE))
b4=best[0][1]
print(f"  {'+ лучший четвёртый (выбран на A): '+b4:>34s} {best[0][0]:12.4f} {pB(BASE+[b4]):14.4f}")
sims=[pB(BASE+[c]) for c in rnd.sample([c for c in CAND if c not in BASE], 200)]
sims.sort()
print(f"  {'+ случайный четвёртый, среднее':>34s} {'—':>12s} {sum(sims)/len(sims):14.4f}")
print(f"  {'95-й процентиль случайного на B':>34s} {'—':>12s} {sims[-11]:14.4f}")
ok = pB(BASE+[b4]) < sims[-11]
print(f"\n  четвёртый центр переживает проверку: {'ДА' if ok else 'НЕТ'}")
# жадная тройка с нуля — тоже на A, проверка на B
sel=[]
for _ in range(4):
    c=sorted(((pA(sel+[x]), x) for x in CAND if x not in sel))[0][1]; sel.append(c)
print(f"\n  жадный набор, выбранный на A: {', '.join(sel)}")
print(f"    на A {pA(sel):+.4f}   на B {pB(sel):+.4f}")
print(f"    тройка Тимма + {b4} на B: {pB(BASE+[b4]):+.4f}")
