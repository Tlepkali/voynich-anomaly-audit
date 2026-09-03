import json, collections, random, time, os, sys
D=json.load(open("parsed.json")); rows=D["rows"]
VOY=[w for r in rows if r["locus"]=="P" for w in r["words"] if '?' not in w]
freq=collections.Counter(VOY)
SRC="".join(sorted({c for w in freq for c in w}))
MINLEN=4; LEXN=1900
TOP=[(w,n) for w,n in freq.most_common(1500) if len(w)>=MINLEN]
tot=sum(n for _,n in TOP)
rnd0=random.Random(7)
def scr(w):
    l=list(w); rnd0.shuffle(l); return "".join(l)
CTL=[(scr(w),n) for w,n in TOP]
FILES=[("латынь","ref/latin.clean"),("английский","ref/english.clean"),
       ("итальянский","ref/wiki_it.clean"),("немецкий","ref/wiki_de.clean"),
       ("греческий","ref/wiki_el.clean"),("иврит","ref/wiki_he.clean"),
       ("арабский","ref/wiki_ar.clean"),("турецкий","ref/wiki_tr.clean"),
       ("баскский","ref/wiki_eu.clean"),("финский","ref/wiki_fi.clean"),
       ("грузинский","ref/wiki_ka.clean"),("монгольский","ref/wiki_mn.clean")]
def climb(items, lex, tgt, seed, steps=1500):
    rnd=random.Random(seed)
    perm=list(tgt[:len(SRC)]); rnd.shuffle(perm)
    def sc(p):
        t=str.maketrans(SRC,"".join(p))
        return sum(1 for w,_ in items if w.translate(t) in lex)
    best=sc(perm)
    for _ in range(steps):
        i,j=rnd.randrange(len(SRC)), rnd.randrange(len(SRC))
        if i==j: continue
        perm[i],perm[j]=perm[j],perm[i]
        s=sc(perm)
        if s>=best: best=s
        else: perm[i],perm[j]=perm[j],perm[i]
    return best
print("="*94)
print(f"ПЕРЕБОР ПЕРЕСТАНОВОК ПРОТИВ ДВЕНАДЦАТИ ЯЗЫКОВ (словарь уравнен: {LEXN} самых частых слов ≥{MINLEN} знаков)")
print("="*94)
print(f"  {'язык':14s} {'алфавит':>8s} {'лучшее (типов)':>15s} {'контроль':>10s} {'превышение':>12s} {'доля типов':>12s}")
res=[]
t0=time.time()
for lab,path in FILES:
    if not os.path.exists(path): continue
    txt=open(path).read()
    cnt=collections.Counter(w for w in txt.split() if len(w)>=MINLEN)
    lex={w for w,_ in cnt.most_common(LEXN)}
    alpha="".join(sorted({c for c in txt if c!=' '}))
    if len(alpha)<len(SRC): continue
    r=max(climb(TOP,lex,alpha,100+k) for k in range(3))
    c=max(climb(CTL,lex,alpha,200+k) for k in range(3))
    res.append((r/max(1,c), lab, r, c, len(alpha)))
    print(f"  {lab:14s} {len(alpha):8d} {r:15d} {c:10d} {r/max(1,c):11.2f}× {r/len(TOP):11.2%}")
print(f"\n  время {time.time()-t0:.0f} с;  типов в работе {len(TOP)}")
res.sort(reverse=True)
print("\n  по превышению над контролем:")
for k,lab,r,c,a in res: print(f"     {lab:14s} {k:.2f}×  (реально {r}, контроль {c})")
