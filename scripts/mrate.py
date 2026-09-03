import json, random, collections, sys
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
SEC={"H":"травник","P":"аптечный","B":"«банный»","T":"только текст","C":"космол.","S":"рецепты"}
LINES=[]
for r in [r for r in rows if r["locus"]=="P"]:
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=3:
        m=pages.get(r["page"],{})
        LINES.append({"w":ws,"page":r["page"],"L":m.get("L","?"),"I":m.get("I","?"),"H":m.get("H","?")})

def stats(ls):
    """возвращает по каждой СТРАНИЦЕ счётчики, чтобы бутстрэпить страницами"""
    byp=collections.defaultdict(lambda: [0,0,0,0,0,0])  # end_m, end_n, mid_m, mid_n, glyph_m, glyph_n
    for l in ls:
        p=byp[l["page"]]
        p[1]+=1; p[0]+= l["w"][-1].endswith('m')
        for w in l["w"][:-1]:
            p[3]+=1; p[2]+= w.endswith('m')
        for w in l["w"]:
            p[5]+=len(w); p[4]+= w.count('m')
    return list(byp.values())
def agg(ps):
    s=[sum(p[i] for p in ps) for i in range(6)]
    end = s[0]/s[1] if s[1] else 0
    mid = s[2]/s[3] if s[3] else 0
    gly = s[4]/s[5] if s[5] else 0
    return end, mid, (end/mid if mid else float('inf')), gly
def boot(ps, idx, n=4000, seed=23):
    rnd=random.Random(seed); N=len(ps); r=[]
    for _ in range(n):
        smp=[ps[rnd.randrange(N)] for _ in range(N)]
        r.append(agg(smp)[idx])
    r.sort(); return agg(ps)[idx], r[int(.025*n)], r[int(.975*n)]

CELLS=[("рука 1","H","A"),("рука 1","P","A"),("рука 2","B","B"),("рука 2","H","B"),
       ("рука 2","T","B"),("рука 3","S",None),("рука 3","H",None),("рука 5","H","B")]
def sel(h,s,L):
    return [l for l in LINES if l["H"]==h.split()[-1] and l["I"]==s and (L is None or l["L"]==L)]

print("="*104)
print("ЗНАК m: в конце строки, в середине строки, и во всём тексте")
print("интервалы — бутстрэп ПО СТРАНИЦАМ")
print("="*104)
print(f"  {'ячейка':24s} {'стр-ц':>6s} {'m в конце строки':>24s} {'m в середине':>19s} {'перевес':>8s} {'m/1000 знаков':>14s}")
store={}
for h,s,L in CELLS:
    ls=sel(h,s,L)
    if len(ls)<55: continue
    ps=stats(ls); store[(h,s)]=ps
    e,elo,ehi=boot(ps,0); m,mlo,mhi=boot(ps,1); _,_,ratio,gly=agg(ps)
    print(f"  {h+' · '+SEC.get(s,s):24s} {len(ps):6d} {e:9.1%} [{elo:5.1%},{ehi:5.1%}] "
          f"{m:8.2%} [{mlo:5.2%},{mhi:5.2%}] {ratio:8.1f}× {1000*gly:14.1f}")

print("\n"+"="*104)
print("ПРЯМЫЕ СРАВНЕНИЯ доли m в конце строки (бутстрэп разности по страницам)")
print("="*104)
def diff(a,b,label,idx=0,n=4000,seed=71):
    pa,pb=store[a],store[b]
    rnd=random.Random(seed); r=[]
    for _ in range(n):
        sa=[pa[rnd.randrange(len(pa))] for _ in range(len(pa))]
        sb=[pb[rnd.randrange(len(pb))] for _ in range(len(pb))]
        r.append(agg(sa)[idx]-agg(sb)[idx])
    r.sort(); lo,hi=r[int(.025*n)],r[int(.975*n)]
    d=agg(pa)[idx]-agg(pb)[idx]
    mark="различаются ✓" if (lo>0 or hi<0) else "не различаются ·"
    print(f"  {label:52s} {d:+7.1%} [{lo:+6.1%}, {hi:+6.1%}]  {mark}")

print("  — внутри одной руки 2 —")
diff(("рука 2","B"),("рука 2","H"),"«банный» − травник (обе рукой 2)")
diff(("рука 2","B"),("рука 2","T"),"«банный» − только текст (обе рукой 2)")
print("  — против других рук в языке B —")
diff(("рука 2","B"),("рука 3","S"),"«банный» (рука 2) − рецепты (рука 3)")
diff(("рука 2","B"),("рука 5","H"),"«банный» (рука 2) − травник (рука 5)")
print("  — то же по СЕРЕДИНЕ строки: если и там разрыв, дело в словаре, а не в строке —")
diff(("рука 2","B"),("рука 2","H"),"«банный» − травник, m в СЕРЕДИНЕ строки", idx=1)
diff(("рука 2","B"),("рука 3","S"),"«банный» − рецепты, m в СЕРЕДИНЕ строки", idx=1)
print("  — и перевес «конец против середины» —")
diff(("рука 2","B"),("рука 2","H"),"«банный» − травник, ПЕРЕВЕС конец/середина", idx=2)
diff(("рука 2","B"),("рука 3","S"),"«банный» − рецепты, ПЕРЕВЕС конец/середина", idx=2)
