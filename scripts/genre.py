import re, collections, math, random, sys
sys.path.insert(0,"."); import metrics
alt=re.compile(r'\[([^\]]*)\]')
def clean(t):
    t=re.sub(r'<[^>]*>','',t); t=re.sub(r'\{[^}]*\}','',t)
    t=alt.sub(lambda m:m.group(1).split(':')[0],t)
    t=re.sub(r'@\d+;','',t).replace("'","").replace('!','').replace('%','')
    return re.sub(r'[-=~/]','',t.replace(',','.'))
PARA=[]; cur=[]
for line in open("ZL3b-n.txt", encoding="utf-8", errors="replace"):
    m=re.match(r'^<f[0-9]+[rv][0-9]*\.[0-9]+,[@+=*&]P[A-Za-z0-9]?>\s*(.*)$', line)
    if not m: continue
    txt=m.group(1); ws=[w for w in clean(txt).split('.') if w and '?' not in w]
    if len(ws)>=3: cur.append(ws)
    if '<$>' in txt:
        if len(cur)>=2: PARA.append(cur)
        cur=[]
if len(cur)>=2: PARA.append(cur)
LINES=[l for p in PARA for l in p]
def gl(w): return metrics.merge(w)
def mean(x): return sum(x)/len(x) if x else 0
print(f"абзацев с 2+ строками: {len(PARA)}, строк: {len(LINES)}\n")

print("="*76); print("ПРИЗНАК ПОЭЗИИ 1: рифма — совпадают ли концы соседних строк"); print("="*76)
def rhyme(depth, adjacent=True, seed=1):
    hit=0; tot=0
    for p in PARA:
        ends=[tuple(gl(l[-1])[-depth:]) for l in p]
        for i in range(len(ends)-1):
            tot+=1; hit += (ends[i]==ends[i+1])
    return hit, tot
for depth in (1,2):
    h,t=rhyme(depth)
    # контроль: перемешиваем концовки между всеми строками
    ends=[tuple(gl(l[-1])[-depth:]) for l in LINES]
    rnd=random.Random(3); exp=[]
    for _ in range(400):
        e=ends[:]; rnd.shuffle(e)
        k=0; hh=0; tt=0
        for p in PARA:
            seg=e[k:k+len(p)]; k+=len(p)
            for i in range(len(seg)-1): tt+=1; hh+= (seg[i]==seg[i+1])
        exp.append(hh/tt)
    exp.sort()
    print(f"  совпадение последних {depth} знак(ов): факт {h/t:6.1%}   "
          f"случайно {mean(exp):6.1%} (95% до {exp[380]:.1%})   "
          f"{'ВЫШЕ ✓' if h/t>exp[380] else 'не выше ·'}")

print("\n"+"="*76); print("ПРИЗНАК ПОЭЗИИ 2: размер — насколько ровны строки"); print("="*76)
for name, f in (("слов в строке", lambda l: len(l)), ("знаков в строке", lambda l: sum(len(gl(w)) for w in l))):
    within=[]
    for p in PARA:
        if len(p)<3: continue
        v=[f(l) for l in p]; m=mean(v)
        within.append((mean([(x-m)**2 for x in v])**0.5)/m)
    print(f"  {name:18s} разброс внутри абзаца (CV): {mean(within):.3f}")
lat=open("ref/latin.clean").read().split(); eng=open("ref/english.clean").read().split()
def fake(ws, sizes):
    o=[];k=0
    for p in sizes:
        blk=[]
        for s in p:
            blk.append(ws[k:k+s]); k+=s
        o.append(blk)
    return o
sizes=[[len(l) for l in p] for p in PARA]
for nm,ws in (("латынь",lat),("английский",eng)):
    P2=fake(ws,sizes); within=[]
    for p in P2:
        if len(p)<3: continue
        v=[sum(len(w) for w in l) for l in p]; m=mean(v)
        if m: within.append((mean([(x-m)**2 for x in v])**0.5)/m)
    print(f"  {nm:18s} тот же разброс по буквам:  {mean(within):.3f}")

print("\n"+"="*76); print("ПРИЗНАК СПИСКА: похожи ли строки одного абзаца друг на друга"); print("="*76)
def linesim(a,b):
    sa=set(a); sb=set(b)
    return len(sa&sb)/min(len(sa),len(sb))
same=[]; cross=[]
rnd=random.Random(7)
for p in PARA:
    for i in range(len(p)-1): same.append(linesim(p[i],p[i+1]))
for _ in range(4000):
    a=rnd.choice(LINES); b=rnd.choice(LINES)
    if a is not b: cross.append(linesim(a,b))
print(f"  доля общих слов у соседних строк ОДНОГО абзаца: {mean(same):.3f}")
print(f"  у случайных строк из разных мест:               {mean(cross):.3f}")
print(f"  отношение: {mean(same)/mean(cross):.2f}×")
for nm,ws in (("латынь",lat),("английский",eng)):
    P2=fake(ws,sizes); s2=[];c2=[]
    L2=[l for p in P2 for l in p]
    for p in P2:
        for i in range(len(p)-1): 
            if p[i] and p[i+1]: s2.append(linesim(p[i],p[i+1]))
    for _ in range(4000):
        a=rnd.choice(L2); b=rnd.choice(L2)
        if a and b and a is not b: c2.append(linesim(a,b))
    print(f"  {nm:12s} свои {mean(s2):.3f}  чужие {mean(c2):.3f}  отношение {mean(s2)/mean(c2):.2f}×")
