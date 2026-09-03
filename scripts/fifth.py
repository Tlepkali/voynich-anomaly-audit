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
print("  матрица расстояний…")
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
print("="*100); print("СКОЛЬКО ЦЕНТРОВ: отбор на половине A, проверка на отложенной B"); print("="*100)
print(f"  {'k':>3s} {'добавлен':>12s} {'на A':>9s} {'на B':>9s} {'прирост на B':>13s} {'случайный k-й на B':>19s}")
sel=[]; prevB=0.0
for k in range(1,9):
    best=sorted(((pA(sel+[c]), c) for c in CAND if c not in sel))[0]
    sel.append(best[1])
    b=pB(sel)
    pool=[c for c in CAND if c not in sel[:-1]]
    sims=sorted(pB(sel[:-1]+[c]) for c in rnd.sample(pool, 120))
    gain=b-prevB
    mark=""
    if b<sims[10]: mark="  значимо"
    elif b<sims[30]: mark="  на грани"
    else: mark="  ШУМ"
    print(f"  {k:>3d} {best[1]:>12s} {best[0]:9.4f} {b:9.4f} {gain:13.4f} {sum(sims)/len(sims):19.4f}{mark}")
    prevB=b
print("\n  «значимо» = результат вне лучших 8 % случайных наборов того же размера")
print("\n" + "="*100); print("ПЯТЫЙ ПОВЕРХ ЧЕТЫРЁХ УСТАНОВЛЕННЫХ (daiin, ol, chedy, qokedy)"); print("="*100)
BASE4=["daiin","ol","chedy","qokedy"]
p4A, p4B = pA(BASE4), pB(BASE4)
best5=sorted(((pA(BASE4+[c]), c) for c in CAND if c not in BASE4))[:6]
sims5=sorted(pB(BASE4+[c]) for c in rnd.sample([c for c in CAND if c not in BASE4],150))
print(f"  четыре центра: на A {p4A:.4f}, на B {p4B:.4f}")
print(f"\n  {'кандидат в пятые':>18s} {'на A':>9s} {'на B':>9s}")
for pa,c in best5:
    print(f"  {c:>18s} {pa:9.4f} {pB(BASE4+[c]):9.4f}")
print(f"\n  случайный пятый на B: среднее {sum(sims5)/len(sims5):.4f}, 95-й процентиль {sims5[7]:.4f}")
top=pB(BASE4+[best5[0][1]])
print(f"  лучший пятый ({best5[0][1]}) на B: {top:.4f} → {'ПРОХОДИТ' if top<sims5[7] else 'НЕ ПРОХОДИТ'}")
