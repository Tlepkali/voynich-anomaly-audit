import json, collections, random, time, sys
D=json.load(open("parsed.json")); rows=D["rows"]
VOY=[w for r in rows if r["locus"]=="P" for w in r["words"] if '?' not in w]
freq=collections.Counter(VOY)
SRC="".join(sorted({c for w in freq for c in w}))
MINLEN=4                                  # короткие слова не засчитываем
TOP=[(w,n) for w,n in freq.most_common(4000) if len(w)>=MINLEN]
LEX=set()
for f in ("ref/latin.clean","ref/scr_vulgata.clean","ref/g_apicius.clean"):
    try: LEX |= {w for w in open(f).read().split() if len(w)>=MINLEN}
    except FileNotFoundError: pass
TGT="abcdefghiklmnopqrstuvxyz"             # 24 латинских буквы
while len(TGT)<len(SRC): TGT+="jw"[len(TGT)-24]
print(f"  знаков EVA: {len(SRC)}, целевых букв: {len(TGT)}, БИЕКЦИЯ")
print(f"  типов (длина ≥{MINLEN}): {len(TOP)}, латинский словарь: {len(LEX)}")
tot=sum(n for _,n in TOP)
def score(perm, items):
    t=str.maketrans(SRC, perm)
    return sum(n for w,n in items if w.translate(t) in LEX)
def climb(items, seed, steps=6000):
    rnd=random.Random(seed)
    perm=list(TGT[:len(SRC)]); rnd.shuffle(perm)
    best=score("".join(perm), items)
    for _ in range(steps):
        i,j=rnd.randrange(len(SRC)), rnd.randrange(len(SRC))
        if i==j: continue
        perm[i],perm[j]=perm[j],perm[i]
        sc=score("".join(perm), items)
        if sc>=best: best=sc
        else: perm[i],perm[j]=perm[j],perm[i]
    return best, "".join(perm)
rnd=random.Random(7)
def scr(w):
    l=list(w); rnd.shuffle(l); return "".join(l)
CTL=[(scr(w),n) for w,n in TOP]
t0=time.time()
print("\n  восхождение к вершине, 10 перезапусков на каждый набор…")
real=sorted((climb(TOP,100+k)[0] for k in range(10)), reverse=True)
ctl =sorted((climb(CTL,200+k)[0] for k in range(10)), reverse=True)
print(f"  время {time.time()-t0:.0f} с\n")
print("="*80)
print("ЛУЧШАЯ ПЕРЕСТАНОВКА АЛФАВИТА EVA (шифр простой замены)")
print("="*80)
print(f"  {'':38s} {'лучшее':>8s} {'медиана':>9s} {'доля текста':>12s}")
print(f"  {'настоящий текст':38s} {real[0]:8d} {real[5]:9d} {real[0]/tot:11.2%}")
print(f"  {'контроль (буквы в слове перемешаны)':38s} {ctl[0]:8d} {ctl[5]:9d} {ctl[0]/tot:11.2%}")
print(f"\n  превышение настоящего над контролем: {real[0]/max(1,ctl[0]):.2f}×")
b,perm=max((climb(TOP,300+k) for k in range(5)), key=lambda x:x[0])
t=str.maketrans(SRC,perm)
hits=sorted(((w.translate(t),n,w) for w,n in TOP if w.translate(t) in LEX), key=lambda x:-x[1])
print(f"\n  лучшая подстановка: {SRC}\n                  →   {perm}")
print(f"  попало в словарь: {len(hits)} типов из {len(TOP)} ({b/tot:.1%} текста)")
print("  самые частые «прочтения»:")
for lt,n,ev in hits[:12]: print(f"     {ev:12s} → {lt:12s} ×{n}")
