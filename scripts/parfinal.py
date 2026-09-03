import re, collections, random, math, sys
sys.path.insert(0,"."); import metrics
alt=re.compile(r'\[([^\]]*)\]')
def clean(t):
    t=re.sub(r'<[^>]*>','',t); t=re.sub(r'\{[^}]*\}','',t)
    t=alt.sub(lambda m:m.group(1).split(':')[0],t)
    t=re.sub(r'@\d+;','',t).replace("'","").replace('!','').replace('%','')
    t=t.replace(',','.'); return re.sub(r'[-=~/]','',t)
LINES=[]
for line in open("ZL3b-n.txt", encoding="utf-8", errors="replace"):
    m=re.match(r'^<(f[0-9]+[rv][0-9]*)\.([0-9]+),([@+=*&])(P)([A-Za-z0-9]?)>\s*(.*)$', line)
    if not m: continue
    page,ln,pos,lt,sub,txt=m.groups()
    ws=[w for w in clean(txt).split('.') if w and '?' not in w]
    if len(ws)>=3:
        LINES.append({"page":page,"w":ws,"sub":sub,"parfinal":'<$>' in txt})
print(f"строк абзацного текста: {len(LINES)}   из них завершают абзац: {sum(1 for l in LINES if l['parfinal'])}")
def mean(x): return sum(x)/len(x) if x else 0.0
def bootpage(items, fn, n=3000, seed=5):
    byp=collections.defaultdict(list)
    for it in items: byp[it["page"]].append(it)
    ps=list(byp.values()); rnd=random.Random(seed); r=[]
    for _ in range(n):
        smp=[x for _ in range(len(ps)) for x in ps[rnd.randrange(len(ps))]]
        r.append(fn(smp))
    r.sort(); return fn(items), r[int(.025*n)], r[int(.975*n)]

mid   =[{"page":l["page"],"w":w} for l in LINES for w in l["w"][1:-1]]
tomarg=[{"page":l["page"],"w":l["w"][-1]} for l in LINES if not l["parfinal"]]
nomarg=[{"page":l["page"],"w":l["w"][-1]} for l in LINES if l["parfinal"]]
special=[{"page":l["page"],"w":l["w"][-1]} for l in LINES if l["sub"] in ("c","r","t")]

print("\n"+"="*88)
print("ПРОВЕРКА: доходит строка до правого поля или нет")
print("="*88)
print(f"  {'группа':40s} {'слов':>6s} {'длина слова':>22s} {'доля на m':>20s}")
for name, grp in (("середина строки (эталон)", mid),
                  ("конец строки, ИДЁТ до поля", tomarg),
                  ("конец строки, ЗАВЕРШАЕТ абзац", nomarg),
                  ("…из них особо размещённые (Pc/Pr/Pt)", special)):
    if len(grp)<15: continue
    L,llo,lhi = bootpage(grp, lambda g: mean([len(metrics.merge(x["w"])) for x in g]))
    M,mlo,mhi = bootpage(grp, lambda g: mean([1 if x["w"].endswith('m') else 0 for x in g]), seed=7)
    print(f"  {name:40s} {len(grp):6d} {L:8.2f} [{llo:.2f},{lhi:.2f}] {M:11.1%} [{mlo:.1%},{mhi:.1%}]")

print("\n"+"="*88)
print("РАЗНОСТЬ «идёт до поля» минус «завершает абзац» (бутстрэп по страницам)")
print("="*88)
def diff(a,b,fn,n=3000,seed=11):
    ba=collections.defaultdict(list); bb=collections.defaultdict(list)
    for x in a: ba[x["page"]].append(x)
    for x in b: bb[x["page"]].append(x)
    pa=list(ba.values()); pb=list(bb.values()); rnd=random.Random(seed); r=[]
    for _ in range(n):
        sa=[x for _ in range(len(pa)) for x in pa[rnd.randrange(len(pa))]]
        sb=[x for _ in range(len(pb)) for x in pb[rnd.randrange(len(pb))]]
        r.append(fn(sa)-fn(sb))
    r.sort(); return fn(a)-fn(b), r[int(.025*n)], r[int(.975*n)]
d,lo,hi=diff(tomarg,nomarg, lambda g: mean([len(metrics.merge(x["w"])) for x in g]))
print(f"  длина последнего слова: {d:+.3f} знака [{lo:+.3f}, {hi:+.3f}]  "
      f"{'различаются ✓' if (lo>0 or hi<0) else 'не различаются ·'}")
d,lo,hi=diff(tomarg,nomarg, lambda g: mean([1 if x['w'].endswith('m') else 0 for x in g]), seed=13)
print(f"  доля слов на m:         {d:+.1%} [{lo:+.1%}, {hi:+.1%}]  "
      f"{'различаются ✓' if (lo>0 or hi<0) else 'не различаются ·'}")
