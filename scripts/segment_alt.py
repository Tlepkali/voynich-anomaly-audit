# -*- coding: utf-8 -*-
"""Пробел как допущение: что выживет, если довериться сомнению транскриптора.
В ZL 18,4 % пробелов помечены запятой как СОМНИТЕЛЬНЫЕ; мой парсер делал из них
обычные пробелы. Здесь строю разбор, где они НЕ пробелы, и сравниваю ядро мер."""
import re, json, collections, random, statistics as st, math
page_re=re.compile(r'^<(f[0-9]+[rv][0-9]*)>\s*(.*)$')
line_re=re.compile(r'^<(f[0-9]+[rv][0-9]*)\.(\d+),([@+=*&])([A-Za-z])([A-Za-z0-9]?)>\s*(.*)$')
alt_re=re.compile(r'\[([^\]]*)\]')
def clean(t, comma):
    t=re.sub(r'<[^>]*>','',t); t=re.sub(r'\{[^}]*\}','',t)
    t=alt_re.sub(lambda m:m.group(1).split(':')[0], t)
    t=re.sub(r'@\d+;','',t)
    t=t.replace("'",'').replace('!','').replace('%','')
    t=t.replace(',', comma)                       # '.' = пробел (как было), '' = склейка
    t=re.sub(r'[-=~/]','',t)
    return t
def parse(comma):
    rows=[]
    for raw in open("data/ZL3b-n.txt",encoding='utf-8',errors='replace'):
        m=line_re.match(raw.rstrip('\n'))
        if not m: continue
        pg,ln,pm,lt,sub,txt=m.groups()
        ws=[w for w in clean(txt,comma).split('.') if w and '?' not in w]
        if len(ws)>=3 and lt=="P": rows.append(ws)
    return rows
def corr(P):
    xs=[a for a,_ in P]; ys=[b for _,b in P]
    mx,my=st.mean(xs),st.mean(ys)
    n=sum((a-mx)*(b-my) for a,b in zip(xs,ys)); d=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    return n/d if d else 0
def rank_corr(L):
    f=[w for l in L for w in l]; c=collections.Counter(f)
    rk={w:i+1 for i,(w,_) in enumerate(c.most_common())}
    return corr([(math.log(rk[l[i]]),math.log(rk[l[i+1]])) for l in L for i in range(len(l)-1)])
def adj(L,B=8,seed=3):
    o=sum(1 for l in L for i in range(len(l)-1) if l[i]==l[i+1])
    rnd=random.Random(seed); acc=0.0
    for _ in range(B):
        for l in L:
            p=rnd.sample(l,len(l)); acc+=sum(1 for a,b in zip(p,p[1:]) if a==b)/B
    return o/max(acc,.01)
def nbrs(T):
    idx=collections.defaultdict(set)
    for w in T:
        idx[w].add(w)
        for i in range(len(w)): idx[w[:i]+w[i+1:]].add(w)
    nb=collections.defaultdict(set)
    for _,ws in idx.items():
        ws=list(ws)
        for i in range(len(ws)):
            for j in range(i+1,len(ws)):
                a,b=ws[i],ws[j]
                if abs(len(a)-len(b))<=1: nb[a].add(b); nb[b].add(a)
    return nb
def dens(T):
    T=set(T); nb=nbrs(T); m=st.mean(len(nb.get(w,())) for w in T)
    def at(d):
        g=[len(nb.get(w,())) for w in T if len(w)==d]
        return st.mean(g) if len(g)>=15 else float('nan')
    a,b=at(3),at(5)
    return m,(b/a if a==a and b==b and a>0 else float('nan'))
def mi(pairs):
    j=collections.Counter(pairs); a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
    n=len(pairs); return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
def junc1(L,seed=9):
    pr=lambda LL:[(x[-1:],y[:1]) for l in LL for x,y in zip(l,l[1:])]
    o=mi(pr(L)); f=[w for l in L for w in l]; rnd=random.Random(seed); s=0.0
    for _ in range(5):
        sh=f[:]; rnd.shuffle(sh); i=0; SH=[]
        for l in L: SH.append(sh[i:i+len(l)]); i+=len(l)
        s+=mi(pr(SH))/5
    return o-s
def mi4(T):
    sub=[w for w in T if len(w)==4]
    if len(sub)<150: return float('nan')
    j=collections.Counter()
    for w in sub:
        for i,c in enumerate(w): j[(c,i)]+=1
    n=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (g,i),c in j.items(): pg[g]+=c; pp[i]+=c
    return sum(c/n*math.log2((c/n)/((pg[g]/n)*(pp[i]/n))) for (g,i),c in j.items())
def slot_exc(T,B=8):
    o=mi4(T)
    if o!=o: return float('nan')
    v=[]
    for s in range(B):
        r=random.Random(50+s); sh=[]
        for w in T:
            c=list(w); r.shuffle(c); sh.append("".join(c))
        x=mi4(sh)
        if x==x: v.append(x)
    return o/st.mean(v) if v else float('nan')
def markov(types, order, counts, seed=0):
    rnd=random.Random(seed); tr=collections.defaultdict(collections.Counter)
    for w in types:
        s="^"*order+w+"$"
        for i in range(order,len(s)): tr[s[i-order:i]][s[i]]+=1
    pools={k:[c for c,n in v.items() for _ in range(n)] for k,v in tr.items()}
    want=collections.Counter(len(w) for w in types); got=collections.Counter()
    out=set(); guard=0
    while len(out)<len(types) and guard<len(types)*200:
        guard+=1; ctx="^"*order; w=""
        while True:
            p_=pools.get(ctx)
            if not p_: break
            c=p_[rnd.randrange(len(p_))]
            if c=="$": break
            w+=c; ctx=(ctx+c)[-order:]
            if len(w)>25: break
        if not w or w in out or got[len(w)]>=want.get(len(w),0): continue
        out.add(w); got[len(w)]+=1
    return sorted(out)
print("="*104); print("ПРОБЕЛ КАК ДОПУЩЕНИЕ: 18,4 % пробелов помечены транскриптором как сомнительные"); print("="*104)
rows=[]
for comma,lab in [('.', 'сомнительные = ПРОБЕЛ (как считалось)'), ('', 'сомнительные = СКЛЕЙКА')]:
    L=parse(comma); T=sorted({w for l in L for w in l}); f=[w for l in L for w in l]
    m,sh=dens(T)
    M=markov(T,2,None,0)
    regen=len(set(M)&set(T))/max(len(M),1)
    rows.append(dict(lab=lab,n=len(f),ty=len(T),ml=st.mean(len(w) for w in f),
        rc=rank_corr(L), adj=adj(L), dens=m, shape=sh, j=junc1(L), slot=slot_exc(T), regen=regen))
print(f"  {'мера':>34s} {'пробел':>12s} {'склейка':>12s} {'изменение':>12s}")
A,B=rows
def row(nm,k,fmt="%.3f",pct=False):
    a,b=A[k],B[k]
    f=lambda x: (f"{x:.1%}" if pct else fmt%x) if x==x else "—"
    ch=f"{(b-a)/abs(a)*100:+.0f} %" if (a==a and b==b and a) else "—"
    print(f"  {nm:>34s} {f(a):>12s} {f(b):>12s} {ch:>12s}")
row("токенов","n","%d"); row("типов","ty","%d"); row("средняя длина слова","ml","%.2f")
row("ранг-корреляция соседей","rc","%+.4f")
row("соседство одинаковых","adj","%.2f")
row("плотность окрестности","dens","%.2f")
row("форма дл5/дл3","shape","%.2f")
row("стык по 1 знаку","j","%.3f")
row("слотовость (типы, дл4)","slot","%.2f")
row("порождение цепью","regen",pct=True)
