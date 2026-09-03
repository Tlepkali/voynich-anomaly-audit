# -*- coding: utf-8 -*-
"""Жанровый сдвиг: скрейп Википедии против книги НА ТОМ ЖЕ ЯЗЫКЕ, равные объёмы."""
import json, collections, statistics as st, math, random, os
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]; LENS=[len(l) for l in VL]
def relines(f):
    out=[];k=0
    for n in LENS:
        if k+n>len(f): break
        out.append(f[k:k+n]); k+=n
    return out
def corr(P):
    xs=[a for a,_ in P]; ys=[b for _,b in P]
    mx,my=st.mean(xs),st.mean(ys)
    n=sum((a-mx)*(b-my) for a,b in zip(xs,ys)); d=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    return n/d if d else 0
def rc(L):
    f=[w for l in L for w in l]; c=collections.Counter(f)
    rk={w:i+1 for i,(w,_) in enumerate(c.most_common())}
    return corr([(math.log(rk[l[i]]),math.log(rk[l[i+1]])) for l in L for i in range(len(l)-1)])
def at(path,n=34000,B=10,seed=7):
    if not os.path.exists(path): return None
    f=open(path,encoding="utf-8",errors="ignore").read().split()
    if len(f)<n: return None
    v=[rc(relines(f[random.Random(seed+b).randrange(0,len(f)-n+1):][:n])) for b in range(B)]
    return st.mean(v), st.stdev(v), len(f)
PAIRS=[("английский","ref/wiki_en.clean",["ref/bk_en1.clean","ref/bk_en2.clean","ref/english.clean"]),
       ("испанский","ref/wiki_es.clean",["ref/bk_es.clean"]),
       ("французский","ref/wiki_fr.clean",["ref/bk_fr1.clean","ref/bk_fr2.clean"]),
       ("итальянский","ref/wiki_it.clean",["ref/bk_it.clean"]),
       ("иврит","ref/wiki_he.clean",["ref/scr_tanakh.clean"])]
print("="*104); print("ЖАНРОВЫЙ СДВИГ: Википедия против книги на том же языке, по 34 тыс. слов"); print("="*104)
print(f"  {'язык':>14s} {'Википедия':>12s} {'книги':>28s} {'сдвиг вики−книга':>18s}")
diffs=[]
for lang,wp,bks in PAIRS:
    w=at(wp)
    bs=[(os.path.basename(b)[:-6], at(b)) for b in bks]
    bs=[(n,r) for n,r in bs if r]
    if not w or not bs:
        print(f"  {lang:>14s}  — не хватает данных ({'нет вики' if not w else 'нет книг'})"); continue
    bm=st.mean(r[0] for _,r in bs)
    d=w[0]-bm; diffs.append(d)
    detail=", ".join(f"{n} {r[0]:+.3f}" for n,r in bs)
    print(f"  {lang:>14s} {w[0]:+12.4f} {bm:+10.4f}  ({detail})".ljust(84)+f"{d:+8.4f}")
if diffs:
    m=st.mean(diffs)
    print(f"\n  СРЕДНИЙ ЖАНРОВЫЙ СДВИГ: {m:+.4f}  (разброс {min(diffs):+.4f}…{max(diffs):+.4f}, n={len(diffs)})")
    mn=at("ref/wiki_mn.clean")
    V=[w for l in VL for w in l]
    vv=st.mean(rc(relines(V[random.Random(7+b).randrange(0,len(V)-34000+1):][:34000])) for b in range(10)) if len(V)>=34000 else None
    if mn:
        print(f"\n  монгольский (Википедия) на 34k: {mn[0]:+.4f}")
        print(f"  с поправкой на жанр:            {mn[0]-m:+.4f}")
        print(f"  ВОЙНИЧ (книга) на 34k:          {vv:+.4f}")
        print(f"\n  {'монгольский всё ещё выше' if mn[0]-m>vv else 'ПОСЛЕ ПОПРАВКИ РУКОПИСЬ ВЫШЕ'}")
