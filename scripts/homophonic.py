import json, collections, random, time, os, sys
D=json.load(open("parsed.json")); rows=D["rows"]
VOY=[w for r in rows if r["locus"]=="P" for w in r["words"] if '?' not in w]
freq=collections.Counter(VOY)
SRC=sorted({c for w in freq for c in w})
MINOUT=4; LEXN=2200
TOP=[(w,n) for w,n in freq.most_common(1500) if len(w)>=4]
rnd0=random.Random(13)
def scr(w):
    l=list(w); rnd0.shuffle(l); return "".join(l)
CTL=[(scr(w),n) for w,n in TOP]
MIN_DISTINCT=12; MAX_NULL=5      # защита от вырождения
def apply(m, w):
    return "".join(m[c] for c in w if m[c])
def valid(m):
    vals=[v for v in m.values() if v]
    return len(set(vals))>=MIN_DISTINCT and sum(1 for v in m.values() if not v)<=MAX_NULL
def climb(items, lex, tgt, seed, steps=2500):
    rnd=random.Random(seed)
    opts=list(tgt)+[""]
    m={c: rnd.choice(list(tgt)) for c in SRC}
    def sc(mm):
        if not valid(mm): return -1
        s=0
        for w,n in items:
            o=apply(mm,w)
            if len(o)>=MINOUT and o in lex: s+=1
        return s
    best=sc(m)
    for _ in range(steps):
        c=rnd.choice(SRC); old=m[c]
        m[c]=rnd.choice(opts)
        s=sc(m)
        if s>=best: best=s
        else: m[c]=old
    return best, dict(m)
FILES=[("латынь","ref/latin.clean"),("английский","ref/english.clean"),
       ("немецкий","ref/wiki_de.clean"),("греческий","ref/wiki_el.clean"),
       ("иврит","ref/wiki_he.clean"),("итальянский","ref/wiki_it.clean"),
       ("чешский","ref/wiki_cs.clean"),("польский","ref/wiki_pl.clean"),
       ("исландский","ref/wiki_is.clean"),("шведский","ref/wiki_sv.clean"),
       ("датский","ref/wiki_da.clean"),("русский","ref/wiki_ru.clean")]
print("="*98)
print("МНОГОЗНАЧНЫЙ ШИФР С ПУСТЫШКАМИ: 25 глифов → буквы или ничего")
print(f"защита от вырождения: не меньше {MIN_DISTINCT} разных букв, не больше {MAX_NULL} пустышек")
print("="*98)
print(f"  {'язык':14s} {'типов ≥4':>9s} {'лучшее':>8s} {'контроль':>9s} {'превышение':>11s} {'доля':>8s}")
t0=time.time(); res=[]
for lab,path in FILES:
    if not os.path.exists(path): continue
    cnt=collections.Counter(w for w in open(path).read().split() if len(w)>=MINOUT)
    if len(cnt)<800: 
        print(f"  {lab:14s} словарь мал ({len(cnt)}) — пропуск"); continue
    lex={w for w,_ in cnt.most_common(LEXN)}
    tgt="".join(sorted({c for w in lex for c in w}))
    r=max(climb(TOP,lex,tgt,100+k)[0] for k in range(3))
    c=max(climb(CTL,lex,tgt,200+k)[0] for k in range(3))
    res.append((r/max(1,c),lab,r,c))
    print(f"  {lab:14s} {len(cnt):9d} {r:8d} {c:9d} {r/max(1,c):10.2f}× {r/len(TOP):7.2%}")
print(f"\n  время {time.time()-t0:.0f} с;  типов рукописи в работе: {len(TOP)}")
print("\n  для сравнения — простая замена (биекция) давала 0,45–1,27 % словаря")
