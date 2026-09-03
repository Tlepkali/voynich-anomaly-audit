# -*- coding: utf-8 -*-
import json, collections, math, random, os
D=json.load(open("parsed.json"))
VOY=[w for r in D["rows"] if r["locus"]=="P" for w in r["words"] if '?' not in w]
freq=collections.Counter(VOY)
TYPES=[w for w,n in freq.items() if n>=2]          # хапаксы шумят, берём от двух
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
def corr(x,y):
    n=len(x); mx=sum(x)/n; my=sum(y)/n
    c=sum((a-mx)*(b-my) for a,b in zip(x,y))
    d=math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
    return c/d if d else 0.0
def part(rxy,rxz,ryz):
    return (rxy-rxz*ryz)/math.sqrt(max(1e-12,(1-rxz**2)*(1-ryz**2)))
CENT=["daiin","ol","chedy"]
dmin=[min(lev(w,c) for c in CENT) for w in TYPES]
lf=[math.log(freq[w]) for w in TYPES]
ln=[len(w) for w in TYPES]
r_df=corr(dmin,lf); r_dl=corr(dmin,ln); r_lf=corr(ln,lf)
print("="*96); print("НАБЛЮДЕНИЕ ТИММА: частота против расстояния правки до daiin, ol, chedy"); print("="*96)
print(f"  типов в работе (частота ≥2): {len(TYPES):,}")
print(f"\n  расстояние ↔ log частоты      r = {r_df:+.3f}   ← наблюдение Тимма")
print(f"  расстояние ↔ длина слова      r = {r_dl:+.3f}")
print(f"  длина слова ↔ log частоты     r = {r_lf:+.3f}")
print(f"\n  ЧАСТНАЯ корреляция при фиксированной длине: r = {part(r_df,r_dl,r_lf):+.3f}")
print("\n" + "="*96); print("КОНТРОЛЬ: а если центрами взять три другие частые слова?"); print("="*96)
rnd=random.Random(7)
pool=[w for w,n in freq.most_common(300)]
sims=[]
for _ in range(200):
    c3=rnd.sample(pool,3)
    dm=[min(lev(w,c) for c in c3) for w in TYPES]
    sims.append(corr(dm,lf))
sims.sort()
print(f"  200 случайных троек из 300 самых частых слов:")
print(f"    среднее r = {sum(sims)/len(sims):+.3f}, разброс [{sims[0]:+.3f} … {sims[-1]:+.3f}]")
print(f"    5-й и 95-й процентили: {sims[10]:+.3f} … {sims[-11]:+.3f}")
better=sum(1 for s in sims if s<=r_df)
print(f"    троек не хуже daiin/ol/chedy: {better} из 200 ({better/2:.0f} %)")
print("\n" + "="*96); print("ТО ЖЕ НА ЯЗЫКАХ: центры — три самых частых слова корпуса"); print("="*96)
print(f"  {'корпус':>14s} {'центры':>26s} {'r(расст,частота)':>17s} {'частная по длине':>17s}")
print(f"  {'Войнич':>14s} {'daiin, ol, chedy':>26s} {r_df:16.3f} {part(r_df,r_dl,r_lf):17.3f}")
for tag,lab in (("latin","латынь"),("english","английский"),("wiki_de","немецкий"),("wiki_it","итальянский")):
    p=f"ref/{tag}.clean"
    if not os.path.exists(p): continue
    ws=open(p).read().split(); f2=collections.Counter(ws)
    T2=[w for w,n in f2.items() if n>=2]
    if len(T2)>6000: T2=rnd.sample(T2,6000)
    c3=[w for w,_ in f2.most_common(3)]
    dm=[min(lev(w,c) for c in c3) for w in T2]
    l2=[math.log(f2[w]) for w in T2]; n2=[len(w) for w in T2]
    a,b,c=corr(dm,l2),corr(dm,n2),corr(n2,l2)
    print(f"  {lab:>14s} {', '.join(c3):>26s} {a:16.3f} {part(a,b,c):17.3f}")
