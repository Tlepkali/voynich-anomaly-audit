import re, collections, random, sys
sys.path.insert(0,"."); import metrics
alt=re.compile(r'\[([^\]]*)\]')
def clean(t):
    t=re.sub(r'<[^>]*>','',t); t=re.sub(r'\{[^}]*\}','',t)
    t=alt.sub(lambda m:m.group(1).split(':')[0],t)
    t=re.sub(r'@\d+;','',t).replace("'","").replace('!','').replace('%','')
    return re.sub(r'[-=~/]','',t.replace(',','.'))
LINES=[]
for line in open("ZL3b-n.txt", encoding="utf-8", errors="replace"):
    m=re.match(r'^<(f[0-9]+[rv][0-9]*)\.([0-9]+),([@+=*&])(P)([A-Za-z0-9]?)>\s*(.*)$', line)
    if not m: continue
    page,ln,pos,lt,sub,txt=m.groups()
    ws=[w for w in clean(txt).split('.') if w and '?' not in w]
    if len(ws)>=3: LINES.append({"page":page,"w":ws,"sub":sub,"pf":'<$>' in txt})
print(f"строк: {len(LINES)}, завершают абзац: {sum(1 for l in LINES if l['pf'])}")
CACHE={}
def feat(w):
    if w not in CACHE: CACHE[w]=(len(metrics.merge(w)), 1 if w.endswith('m') else 0)
    return CACHE[w]
def group(sel):
    byp=collections.defaultdict(list)
    for l in LINES:
        for w in sel(l): byp[l["page"]].append(feat(w))
    return [v for v in byp.values() if v]
G={"середина строки (эталон)":       group(lambda l: l["w"][1:-1]),
   "конец строки, ИДЁТ до поля":     group(lambda l: [l["w"][-1]] if not l["pf"] else []),
   "конец строки, ЗАВЕРШАЕТ абзац":  group(lambda l: [l["w"][-1]] if l["pf"] else []),
   "…особо размещённые (Pc/Pr/Pt)":  group(lambda l: [l["w"][-1]] if l["sub"] in ("c","r","t") else [])}
def agg(pages, i): 
    n=0; s=0
    for p in pages:
        for f in p: s+=f[i]; n+=1
    return s/n if n else 0
def boot(pages, i, n=2000, seed=5):
    rnd=random.Random(seed); r=[]
    for _ in range(n):
        smp=[pages[rnd.randrange(len(pages))] for _ in range(len(pages))]
        r.append(agg(smp,i))
    r.sort(); return agg(pages,i), r[int(.025*n)], r[int(.975*n)]
print("\n"+"="*90)
print(f"  {'группа':34s} {'слов':>6s} {'длина последнего слова':>26s} {'доля на m':>20s}")
print("="*90)
for name,pg in G.items():
    cnt=sum(len(p) for p in pg)
    if cnt<15: continue
    L,a,b = boot(pg,0); M,c,d = boot(pg,1,seed=7)
    print(f"  {name:34s} {cnt:6d} {L:10.2f} [{a:.2f}, {b:.2f}] {M:11.1%} [{c:.1%}, {d:.1%}]")
def diff(pa,pb,i,n=2000,seed=11):
    rnd=random.Random(seed); r=[]
    for _ in range(n):
        sa=[pa[rnd.randrange(len(pa))] for _ in range(len(pa))]
        sb=[pb[rnd.randrange(len(pb))] for _ in range(len(pb))]
        r.append(agg(sa,i)-agg(sb,i))
    r.sort(); return agg(pa,i)-agg(pb,i), r[int(.025*n)], r[int(.975*n)]
print("\n  РАЗНОСТЬ «идёт до поля» минус «завершает абзац»:")
for i,lab,fmt in ((0,"длина последнего слова","%+.3f знака"),(1,"доля слов на m","%+.1f%%")):
    d,lo,hi=diff(G["конец строки, ИДЁТ до поля"], G["конец строки, ЗАВЕРШАЕТ абзац"], i, seed=13+i)
    k=100 if i==1 else 1
    mark="различаются ✓" if (lo>0 or hi<0) else "НЕ различаются ·"
    print(f"     {lab:26s} {(fmt % (d*k))!s:>14s}  [{lo*k:+.3f}, {hi*k:+.3f}]   {mark}")
