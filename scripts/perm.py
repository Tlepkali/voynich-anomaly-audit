import json, collections, random, string, sys, time
D=json.load(open("parsed.json")); rows=D["rows"]
VOY=[w for r in rows if r["locus"]=="P" for w in r["words"] if '?' not in w]
freq=collections.Counter(VOY)
TOP=[(w,n) for w,n in freq.most_common(3000)]
SRC="".join(sorted({c for w in freq for c in w}))
print(f"  знаков EVA: {len(SRC)} — {SRC}")
print(f"  типов в работе: {len(TOP)}, покрывают {sum(n for _,n in TOP)/len(VOY):.0%} текста")
# латинский словарь пошире
LEX=set()
for f in ("ref/latin.clean","ref/scr_vulgata.clean","ref/g_apicius.clean"):
    try: LEX |= set(open(f).read().split())
    except FileNotFoundError: pass
print(f"  латинский словарь: {len(LEX)} слов")
TGT="abcdefghilmnopqrstuvx"      # латинские буквы без j k w y z
def score(perm, items):
    t=str.maketrans(SRC, perm)
    s=0
    for w,n in items:
        if w.translate(t) in LEX: s+=n
    return s
def climb(items, seed, steps=3000):
    rnd=random.Random(seed)
    perm=list((TGT*3)[:len(SRC)]); rnd.shuffle(perm); perm="".join(perm)
    best=score(perm, items)
    for _ in range(steps):
        i,j=rnd.randrange(len(SRC)), rnd.randrange(len(SRC))
        if i==j: continue
        p=list(perm); p[i],p[j]=p[j],p[i]
        # иногда меняем букву целиком, а не переставляем
        if rnd.random()<0.3: p[i]=rnd.choice(TGT)
        p="".join(p); sc=score(p, items)
        if sc>=best: best, perm = sc, p
    return best, perm
# контроль: те же слова с перемешанными внутри буквами
rnd=random.Random(5)
def scr(w):
    l=list(w); rnd.shuffle(l); return "".join(l)
CTL=[(scr(w),n) for w,n in TOP]
t0=time.time()
print("\n  поиск лучшей перестановки (восхождение к вершине, 12 перезапусков)…")
real=[climb(TOP,100+k)[0] for k in range(12)]
ctl =[climb(CTL,200+k)[0] for k in range(12)]
tot=sum(n for _,n in TOP)
real.sort(reverse=True); ctl.sort(reverse=True)
print(f"  время: {time.time()-t0:.0f} с\n")
print("="*78)
print("ЛУЧШЕЕ, ЧТО ДАЁТ ПЕРЕСТАНОВКА АЛФАВИТА EVA")
print("="*78)
print(f"  {'':22s} {'лучшее':>10s} {'медиана':>10s} {'доля текста':>13s}")
print(f"  {'настоящий текст':22s} {real[0]:10d} {real[len(real)//2]:10d} {real[0]/tot:12.2%}")
print(f"  {'контроль (буквы в слове перемешаны)':22s} {ctl[0]:10d} {ctl[len(ctl)//2]:10d} {ctl[0]/tot:12.2%}")
print(f"\n  превышение настоящего над контролем: {real[0]/max(1,ctl[0]):.2f}×")
b,perm=max((climb(TOP,300+k) for k in range(4)), key=lambda x:x[0])
t=str.maketrans(SRC, perm)
hits=[(w.translate(t),n) for w,n in TOP if w.translate(t) in LEX]
hits.sort(key=lambda x:-x[1])
print(f"\n  лучшая найденная подстановка: {SRC} → {perm}")
print(f"  «слов», попавших в словарь: {len(hits)} из {len(TOP)}")
print(f"  самые частые: {', '.join(w for w,_ in hits[:18])}")
