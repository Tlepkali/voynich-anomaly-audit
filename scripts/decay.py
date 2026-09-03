# -*- coding: utf-8 -*-
import json, collections, random, os
D=json.load(open("parsed.json"))
pg=collections.defaultdict(list)
for r in D["rows"]:
    if r["locus"]=="P":
        ws=[w for w in r["words"] if '?' not in w]
        if ws: pg[r["page"]].extend(ws)
VPAGES=[v for v in pg.values() if len(v)>=40]
def profile(pages, dmax=200):
    """доля совпадений на расстоянии d, только внутри страницы"""
    hit=collections.Counter(); opp=collections.Counter()
    for p in pages:
        n=len(p)
        for d in range(1,min(dmax,n)):
            k=n-d; opp[d]+=k
            hit[d]+=sum(1 for i in range(k) if p[i]==p[i+d])
    return hit,opp
def shuffled(pages, dmax=200, R=6, seed=3):
    rnd=random.Random(seed); H=collections.Counter(); O=None
    for _ in range(R):
        sh=[rnd.sample(p,len(p)) for p in pages]
        h,o=profile(sh,dmax)
        for d,v in h.items(): H[d]+=v/R
        O=o
    return H,O
BINS=[(1,1),(2,2),(3,3),(4,4),(5,5),(6,7),(8,10),(11,15),(16,20),(21,30),(31,50),(51,80),(81,120),(121,199)]
def agg(hit,opp,lo,hi):
    hh=sum(hit.get(d,0) for d in range(lo,hi+1)); oo=sum(opp.get(d,0) for d in range(lo,hi+1))
    return hh,oo
def report(lab, pages):
    h,o=profile(pages); sh,_=shuffled(pages)
    print(f"\n  {lab}   ({len(pages)} страниц, {sum(len(p) for p in pages):,} слов)")
    print(f"    {'расстояние':>12s} " + " ".join(f"{(str(a) if a==b else f'{a}-{b}'):>7s}" for a,b in BINS))
    obs=[];exp=[]
    for a,b in BINS:
        hh,oo=agg(h,o,a,b); ss,_=agg(sh,o,a,b)
        obs.append(hh/oo if oo else 0); exp.append(ss/oo if oo else 0)
    print(f"    {'наблюдается':>12s} " + " ".join(f"{x*100:7.3f}" for x in obs))
    print(f"    {'случайно':>12s} " + " ".join(f"{x*100:7.3f}" for x in exp))
    print(f"    {'ПРЕВЫШЕНИЕ':>12s} " + " ".join(f"{(o_/e if e else 0):7.2f}" for o_,e in zip(obs,exp)))
print("="*140)
print("ДОКУДА ТЯНЕТСЯ ПЛОСКОСТЬ: доля совпадений слова на расстоянии d, в процентах, только внутри страницы")
print("="*140)
report("ВОЙНИЧ", VPAGES)
for tag,lab in (("latin","ЛАТЫНЬ"),("english","АНГЛИЙСКИЙ"),("wiki_de","НЕМЕЦКИЙ")):
    p=f"ref/{tag}.clean"
    if not os.path.exists(p): continue
    ws=open(p).read().split()
    sizes=[len(x) for x in VPAGES]
    pages=[]; i=0
    for s in sizes:
        if i+s>len(ws): break
        pages.append(ws[i:i+s]); i+=s
    if pages: report(lab, pages)
