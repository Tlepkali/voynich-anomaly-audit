import re, collections, random, math, sys
sys.path.insert(0,"."); import metrics
alt=re.compile(r'\[([^\]]*)\]')
def clean(t):
    t=re.sub(r'<[^>]*>','',t); t=re.sub(r'\{[^}]*\}','',t)
    t=alt.sub(lambda m:m.group(1).split(':')[0],t)
    t=re.sub(r'@\d+;','',t).replace("'","").replace('!','').replace('%','')
    return re.sub(r'[-=~/]','',t.replace(',','.'))
LINES=[]
for line in open("ZL3b-n.txt", encoding="utf-8", errors="replace"):
    m=re.match(r'^<(f[0-9]+[rv][0-9]*)\.([0-9]+),[@+=*&]P[A-Za-z0-9]?>\s*(.*)$', line)
    if not m: continue
    ws=[w for w in clean(m.group(3)).split('.') if w and '?' not in w]
    if len(ws)>=3: LINES.append({"page":m.group(1),"n":int(m.group(2)),"w":ws})
def gl(w): return metrics.merge(w)
# ── графическое устройство знаков (известно из палеографии, не из чтения)
FAMILY={}
for g in ("k","t","p","f"): FAMILY[g]="виселица"
for g in ("ckh","cth","cph","cfh"): FAMILY[g]="скамейчатая виселица"
for g in ("ch","sh"): FAMILY[g]="скамья"
for g in ("e","ee","eee"): FAMILY[g]="ряд e"
for g in ("i","ii","iii","in","iin","iiin","ain","aiin","air","aiir"): FAMILY[g]="ряд минимов"
# пары, отличающиеся ровно одним штрихом
STROKE={("e","ee"),("ee","eee"),("i","ii"),("ii","iii"),("in","iin"),("iin","iiin"),
        ("ain","aiin"),("air","aiir"),("k","ckh"),("t","cth"),("p","cph"),("f","cfh"),
        ("ch","cth"),("ch","ckh"),("ch","cph"),("ch","cfh"),("i","in"),("ii","iin")}
STROKE={tuple(sorted(p)) for p in STROKE}
def subs_between(a,b):
    ga,gb=gl(a),gl(b)
    if len(ga)!=len(gb): return None
    d=[(x,y) for x,y in zip(ga,gb) if x!=y]
    return d[0] if len(d)==1 else None
print("="*80)
print("ТЕСТ 1. Замены в цепочках похожих соседних слов — графически родственны?")
print("="*80)
obs=collections.Counter(); N=0
for l in LINES:
    for a,b in zip(l["w"],l["w"][1:]):
        s=subs_between(a,b)
        if s: obs[tuple(sorted(s))]+=1; N+=1
def score(pairs):
    fam=sum(n for p,n in pairs.items() if FAMILY.get(p[0]) and FAMILY.get(p[0])==FAMILY.get(p[1]))
    strk=sum(n for p,n in pairs.items() if p in STROKE)
    t=sum(pairs.values())
    return fam/t, strk/t, t
f,s,t = score(obs)
print(f"  замен «один знак на другой» между соседними словами: {t}")
print(f"     из них внутри одного графического семейства: {f:.1%}")
print(f"     из них — пары «плюс-минус один штрих»:        {s:.1%}")
# контроль: те же слова, но пары собраны из НЕсоседних слов той же строки
rnd=random.Random(5); nf=[]; ns=[]
for _ in range(200):
    c=collections.Counter()
    for l in LINES:
        w=l["w"]
        for _ in range(len(w)-1):
            i,j=rnd.randrange(len(w)),rnd.randrange(len(w))
            if i==j: continue
            sb=subs_between(w[i],w[j])
            if sb: c[tuple(sorted(sb))]+=1
    if sum(c.values())>50:
        a,b,_=score(c); nf.append(a); ns.append(b)
nf.sort(); ns.sort()
print(f"  контроль (пары НЕсоседних слов той же строки):")
print(f"     семейство: {sum(nf)/len(nf):.1%} (95% до {nf[int(.95*len(nf))]:.1%})   "
      f"{'ВЫШЕ ✓' if f>nf[int(.95*len(nf))] else 'не выше ·'}")
print(f"     штрих:     {sum(ns)/len(ns):.1%} (95% до {ns[int(.95*len(ns))]:.1%})   "
      f"{'ВЫШЕ ✓' if s>ns[int(.95*len(ns))] else 'не выше ·'}")
print("\n  самые частые замены между соседними словами:")
for p,n in obs.most_common(10):
    tag=[]
    if FAMILY.get(p[0]) and FAMILY.get(p[0])==FAMILY.get(p[1]): tag.append(FAMILY[p[0]])
    if p in STROKE: tag.append("один штрих")
    print(f"     {p[0]:5s} ↔ {p[1]:5s} {n:4d}   {', '.join(tag) if tag else '—'}")

print("\n"+"="*80)
print("ТЕСТ 2. Похоже ли слово на то, что стоит ПРЯМО НАД ним")
print("="*80)
def lcp(a,b):
    ga,gb=gl(a),gl(b); n=0
    for x,y in zip(ga,gb):
        if x!=y: break
        n+=1
    return n
above=[]; ctrl=[]; horiz=[]
byp=collections.defaultdict(list)
for l in LINES: byp[l["page"]].append(l)
rnd=random.Random(11)
for pg,ls in byp.items():
    ls.sort(key=lambda x:x["n"])
    for k in range(1,len(ls)):
        prev,cur=ls[k-1],ls[k]
        if cur["n"]!=prev["n"]+1: continue
        for i,w in enumerate(cur["w"]):
            rel=i/max(1,len(cur["w"])-1)
            j=round(rel*(len(prev["w"])-1))
            above.append(lcp(w, prev["w"][j]))                       # прямо над
            ctrl.append(lcp(w, rnd.choice(prev["w"])))               # случайное из строки выше
        for a,b in zip(cur["w"],cur["w"][1:]): horiz.append(lcp(a,b))
m=lambda x: sum(x)/len(x)
def boot(x,y,n=3000,seed=3):
    r=random.Random(seed); out=[]
    for _ in range(n):
        a=sum(x[r.randrange(len(x))] for _ in range(len(x)))/len(x)
        b=sum(y[r.randrange(len(y))] for _ in range(len(y)))/len(y)
        out.append(a-b)
    out.sort(); return m(x)-m(y), out[75], out[2924]
d,lo,hi=boot(above,ctrl)
print(f"  общий начальный кусок со словом ПРЯМО НАД:     {m(above):.4f}  (пар {len(above)})")
print(f"  со случайным словом из строки выше:            {m(ctrl):.4f}")
print(f"  разность {d:+.4f} [{lo:+.4f}, {hi:+.4f}]  "
      f"{'ЕСТЬ вертикальное сходство ✓' if lo>0 else 'вертикального сходства НЕТ ·'}")
print(f"\n  для сравнения — с соседом СЛЕВА по строке:      {m(horiz):.4f}")
