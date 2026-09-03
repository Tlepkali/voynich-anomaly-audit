import json, collections, math, random, re, sys
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
    txt=m.group(1); cur += [w for w in clean(txt).split('.') if w and '?' not in w]
    if '<$>' in txt:
        if len(cur)>=8: PARA.append(cur)
        cur=[]
if len(cur)>=8: PARA.append(cur)
def gaps(seqs):
    g=collections.Counter()
    for s in seqs:
        pos=collections.defaultdict(list)
        for i,w in enumerate(s): pos[w].append(i)
        for w,ps in pos.items():
            for a,b in zip(ps,ps[1:]): g[b-a]+=1
    return g
def shuf(seqs, seed):
    r=random.Random(seed); o=[]
    for s in seqs:
        t=s[:]; r.shuffle(t); o.append(t)
    return o
def report(seqs, label, nsh=8):
    real=gaps(seqs); R=sum(real.values())
    nulls=[gaps(shuf(seqs,200+k)) for k in range(nsh)]
    Ns=[sum(n.values()) for n in nulls]
    print(f"\n  {label}   повторов внутри абзацев: {R}")
    print(f"     {'промежуток':>12s} {'факт':>8s} {'ожид.':>8s} {'отношение':>10s}")
    buckets=[(1,1),(2,2),(3,4),(5,8),(9,16),(17,32),(33,64)]
    for lo,hi in buckets:
        r=sum(real[d] for d in range(lo,hi+1))
        e=sum(sum(n[d] for d in range(lo,hi+1))/N*R for n,N in zip(nulls,Ns))/nsh
        lab=f"{lo}" if lo==hi else f"{lo}–{hi}"
        bar="█"*int(min(3,(r+1)/(e+1))*12)
        print(f"     {lab:>12s} {r:8d} {e:8.0f} {(r+1)/(e+1):9.2f}×  {bar}")
    return real
print("="*72); print("ПРОМЕЖУТКИ МЕЖДУ ПОВТОРАМИ ОДНОГО СЛОВА ВНУТРИ АБЗАЦА"); print("="*72)
V=report(PARA, "ВОЙНИЧ")
sizes=[len(p) for p in PARA]
def chunk(ws):
    o=[];k=0
    for s in sizes:
        if k+s>len(ws): break
        o.append(ws[k:k+s]); k+=s
    return o
lat=open("ref/latin.clean").read().split()[:sum(sizes)]
eng=open("ref/english.clean").read().split()[:sum(sizes)]
report(chunk(lat), "ЛАТЫНЬ")
report(chunk(eng), "АНГЛИЙСКИЙ")
print("\n"+"="*72)
print("ДИАГНОСТИКА отрицательной взаимной информации: число различных пар")
print("="*72)
def pairs_at(seqs,d):
    s_=set(); n=0
    for s in seqs:
        for i in range(len(s)-d): s_.add((s[i],s[i+d])); n+=1
    return len(s_), n
for d in (1,5,12,20):
    pr,n=pairs_at(PARA,d)
    ps=[pairs_at(shuf(PARA,300+k),d)[0] for k in range(4)]
    print(f"  d={d:2d}: различных пар в тексте {pr:6d}, в перемешанном {sum(ps)/len(ps):8.0f}  "
          f"→ {'меньше (смещение занижает ВИ факта)' if pr<sum(ps)/len(ps) else 'больше'}")
