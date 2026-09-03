import json, collections, math, random, sys
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
# абзацы: последовательности слов, разорванные на границах абзацев
PARA=[]; cur=[]
import re
raw=open("ZL3b-n.txt", encoding="utf-8", errors="replace")
alt=re.compile(r'\[([^\]]*)\]')
def clean(t):
    t=re.sub(r'<[^>]*>','',t); t=re.sub(r'\{[^}]*\}','',t)
    t=alt.sub(lambda m:m.group(1).split(':')[0],t)
    t=re.sub(r'@\d+;','',t).replace("'","").replace('!','').replace('%','')
    return re.sub(r'[-=~/]','',t.replace(',','.'))
for line in raw:
    m=re.match(r'^<f[0-9]+[rv][0-9]*\.[0-9]+,[@+=*&]P[A-Za-z0-9]?>\s*(.*)$', line)
    if not m: continue
    txt=m.group(1)
    cur += [w for w in clean(txt).split('.') if w and '?' not in w]
    if '<$>' in txt:
        if len(cur)>=8: PARA.append(cur)
        cur=[]
if len(cur)>=8: PARA.append(cur)
VOY=[w for p in PARA for w in p]
print(f"абзацев: {len(PARA)}, слов: {len(VOY)}, средний абзац {len(VOY)/len(PARA):.0f} слов")

def mi_at(seqs, d):
    j=collections.Counter(); a=collections.Counter(); b=collections.Counter(); n=0
    for s in seqs:
        for i in range(len(s)-d):
            j[(s[i],s[i+d])]+=1; a[s[i]]+=1; b[s[i+d]]+=1; n+=1
    if n<500: return None
    return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
def shuffled(seqs, seed):
    r=random.Random(seed); out=[]
    for s in seqs:
        t=s[:]; r.shuffle(t); out.append(t)
    return out

def curve(seqs, label, dmax=30, nsh=4):
    real=[]; null=[]
    shs=[shuffled(seqs, 100+k) for k in range(nsh)]
    for d in range(1,dmax+1):
        r=mi_at(seqs,d)
        ns=[mi_at(s,d) for s in shs]; ns=[x for x in ns if x is not None]
        if r is None or not ns: break
        real.append(r); null.append(sum(ns)/len(ns))
    corr=[r-n for r,n in zip(real,null)]
    print(f"\n  {label}")
    print(f"     {'d':>3s} {'набл.':>7s} {'перемеш.':>9s} {'ЧИСТАЯ ВИ':>10s}")
    for i,d in enumerate([1,2,3,4,5,8,12,20,30]):
        if d-1<len(corr):
            print(f"     {d:3d} {real[d-1]:7.3f} {null[d-1]:9.3f} {corr[d-1]:10.4f}")
    return corr

cv=curve(PARA, "РУКОПИСЬ ВОЙНИЧА (абзацы)")
lat=open("ref/latin.clean").read().split()[:len(VOY)]
eng=open("ref/english.clean").read().split()[:len(VOY)]
# нарезаем эталоны на куски той же длины, что абзацы
def chunk(ws, sizes):
    out=[]; k=0
    for s in sizes:
        if k+s>len(ws): break
        out.append(ws[k:k+s]); k+=s
    return out
sizes=[len(p) for p in PARA]
cl=curve(chunk(lat,sizes), "ЛАТЫНЬ (Плиний), куски той же длины")
ce=curve(chunk(eng,sizes), "АНГЛИЙСКИЙ, куски той же длины")
print("\n" + "="*72)
print("ЧИСТАЯ ВЗАИМНАЯ ИНФОРМАЦИЯ ПО РАССТОЯНИЮ (бит)")
print("="*72)
print(f"  {'d':>3s} {'Войнич':>10s} {'латынь':>10s} {'английский':>12s}")
for d in (1,2,3,4,5,6,8,10,12,15,20,25,30):
    if d-1<min(len(cv),len(cl),len(ce)):
        print(f"  {d:3d} {cv[d-1]:10.4f} {cl[d-1]:10.4f} {ce[d-1]:12.4f}")
json.dump({"voy":cv,"lat":cl,"eng":ce}, open("mi_curves.json","w"))
