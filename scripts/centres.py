# -*- coding: utf-8 -*-
import json, collections, math, random
D=json.load(open("parsed.json"))
VOY=[w for r in D["rows"] if r["locus"]=="P" for w in r["words"] if '?' not in w]
freq=collections.Counter(VOY)
TYPES=[w for w,n in freq.items() if n>=2]
LF=[math.log(freq[w]) for w in TYPES]
LN=[len(w) for w in TYPES]
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
print(f"  считаю матрицу расстояний {len(CAND)}×{len(TYPES)}…")
M={c:[lev(c,t) for t in TYPES] for c in CAND}
def corr(x,y):
    n=len(x); mx=sum(x)/n; my=sum(y)/n
    c=sum((a-mx)*(b-my) for a,b in zip(x,y))
    d=math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
    return c/d if d else 0.0
R_LF=corr(LN,LF)
def partial(dm):
    a=corr(dm,LF); b=corr(dm,LN)
    return (a-b*R_LF)/math.sqrt(max(1e-12,(1-b*b)*(1-R_LF*R_LF)))
def dmin(cs):
    cols=[M[c] for c in cs]
    return [min(col[i] for col in cols) for i in range(len(TYPES))]
BASE=["daiin","ol","chedy"]
p3=partial(dmin(BASE))
print("="*98); print("ЕСТЬ ЛИ ЧЕТВЁРТЫЙ ЦЕНТР"); print("="*98)
print(f"  три центра Тимма: частная связь {p3:+.4f}\n")
best=[]
for c in CAND:
    if c in BASE: continue
    best.append((partial(dmin(BASE+[c])), c))
best.sort()
rnd=random.Random(3)
sims=[partial(dmin(BASE+[rnd.choice([c for c in CAND if c not in BASE])])) for _ in range(200)]
sims.sort()
print(f"  {'лучшие четвёртые':>20s} {'связь':>9s} {'прирост':>9s}")
for p,c in best[:6]:
    print(f"  {c:>20s} {p:+9.4f} {p-p3:+9.4f}")
print(f"\n  случайный четвёртый: в среднем {sum(sims)/len(sims):+.4f} (прирост {sum(sims)/len(sims)-p3:+.4f})")
print(f"  95-й процентиль случайного: {sims[-11]:+.4f}")
print(f"  лучший ({best[0][1]}) выходит за этот предел: {'ДА' if best[0][0]<sims[-11] else 'нет'}")
print("\n" + "="*98); print("А ЕСЛИ ВЫБИРАТЬ ЦЕНТРЫ С НУЛЯ, ЖАДНО"); print("="*98)
sel=[]; prev=0.0
print(f"  {'шаг':>4s} {'центр':>12s} {'связь':>9s} {'прирост':>9s}")
for step in range(1,9):
    cands=[(partial(dmin(sel+[c])), c) for c in CAND if c not in sel]
    cands.sort()
    p,c=cands[0]; sel.append(c)
    mark="  ← из тройки Тимма" if c in BASE else ""
    print(f"  {step:>4d} {c:>12s} {p:+9.4f} {p-prev:+9.4f}{mark}")
    prev=p
print(f"\n  тройка Тимма даёт {p3:+.4f}; лучшая жадная тройка — {', '.join(sel[:3])}")
