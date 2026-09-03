# -*- coding: utf-8 -*-
import json, collections, random, os, statistics as st
def near(a,b):
    if a==b: return True
    la,lb=len(a),len(b)
    if abs(la-lb)>1: return False
    if la==lb:
        d=0
        for x,y in zip(a,b):
            if x!=y:
                d+=1
                if d>1: return False
        return d==1
    s,l=(a,b) if la<lb else (b,a)
    return any(l[:i]+l[i+1:]==s for i in range(len(l)))
def chains(seq):
    """длины цепочек подряд идущих почти-одинаковых слов"""
    out=collections.Counter(); i=0
    while i<len(seq)-1:
        n=1
        while i+n<len(seq) and near(seq[i+n-1],seq[i+n]): n+=1
        if n>=2: out[min(n,6)]+=1
        i+=max(n-1,1) if n>=2 else 1
    return out
D=json.load(open("parsed.json"))
pg=collections.defaultdict(list)
for r in D["rows"]:
    if r["locus"]=="P":
        ws=[w for w in r["words"] if '?' not in w]
        if ws: pg[r["page"]].extend(ws)
VOY=[w for v in pg.values() for w in v]
rnd=random.Random(5)
def shuf_pages():
    out=[]
    for v in pg.values():
        c=v[:]; rnd.shuffle(c); out.extend(c)
    return out
print("="*98)
print("ПОСЛЕДОВАТЕЛЬНОСТИ ДЖЕКСОНА: цепочки подряд идущих почти-одинаковых слов")
print("="*98)
obs=chains(VOY)
sims=collections.Counter()
R=8
for _ in range(R):
    c=chains(shuf_pages())
    for k,v in c.items(): sims[k]+=v/R
print(f"  {'длина цепочки':>14s} {'наблюдается':>12s} {'при перемешивании':>19s} {'превышение':>12s}")
for n in (2,3,4,5,6):
    o=obs.get(n,0); e=sims.get(n,0)
    r=f"{o/e:11.2f}×" if e>=1 else ("       —" if o==0 else f"{o:>7d} / ~0")
    print(f"  {n if n<6 else '6+':>14} {o:12d} {e:19.1f} {r}")
print(f"\n  всего слов {len(VOY):,}; перемешивание внутри страницы, {R} повторов")
print("\n" + "="*98); print("ТО ЖЕ НА ЯЗЫКАХ (цепочки длины 2 и 3)"); print("="*98)
print(f"  {'корпус':>14s} {'цеп.2 набл.':>12s} {'перемеш.':>10s} {'превыш.':>9s} | {'цеп.3 набл.':>12s} {'перемеш.':>10s} {'превыш.':>9s}")
def report(seq, lab):
    o=chains(seq); sh=seq[:]; rnd.shuffle(sh); e=chains(sh)
    row=[]
    for n in (2,3):
        a=o.get(n,0); b=e.get(n,0)
        row.append((a,b,a/b if b else float('inf') if a else 0))
    print(f"  {lab:>14s} {row[0][0]:12d} {row[0][1]:10d} {row[0][2]:8.2f}× | {row[1][0]:12d} {row[1][1]:10d} {row[1][2]:8.2f}×")
report(VOY,"Войнич")
for tag,lab in (("latin","латынь"),("english","английский"),("wiki_de","немецкий")):
    p=f"ref/{tag}.clean"
    if os.path.exists(p): report(open(p).read().split()[:len(VOY)], lab)
