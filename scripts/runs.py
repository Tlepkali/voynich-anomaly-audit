import re, collections, random, sys
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
    txt=m.group(1); cur+=[w for w in clean(txt).split('.') if w and '?' not in w]
    if '<$>' in txt:
        if len(cur)>=8: PARA.append(cur); 
        cur=[]
if len(cur)>=8: PARA.append(cur)
def gl(w): return metrics.merge(w)
def close(a,b):
    ga,gb=gl(a),gl(b)
    if abs(len(ga)-len(gb))>1: return False
    if len(ga)==len(gb): return sum(x!=y for x,y in zip(ga,gb))<=1
    s,l=(ga,gb) if len(ga)<len(gb) else (gb,ga)
    return any(l[:i]+l[i+1:]==s for i in range(len(l)))
def runs(seqs, pred):
    """длины серий подряд идущих слов, попарно связанных pred"""
    R=collections.Counter()
    for s in seqs:
        run=1
        for a,b in zip(s,s[1:]):
            if pred(a,b): run+=1
            else: R[run]+=1; run=1
        R[run]+=1
    return R
def shuf(seqs,seed):
    r=random.Random(seed); o=[]
    for s in seqs:
        t=s[:]; r.shuffle(t); o.append(t)
    return o
def report(seqs,label,pred,nsh=6):
    R=runs(seqs,pred); N=[runs(shuf(seqs,400+k),pred) for k in range(nsh)]
    print(f"\n  {label}")
    print(f"     {'длина серии':>12s} {'факт':>7s} {'ожид.':>8s} {'отношение':>10s}")
    for L in (2,3,4,5):
        r=sum(v for k,v in R.items() if k==L)
        e=sum(sum(v for k,v in n.items() if k==L) for n in N)/nsh
        if r+e<3: continue
        print(f"     {L:>12d} {r:7d} {e:8.1f} {(r+1)/(e+1):9.2f}×")
    mx=max([k for k,v in R.items() if v>0]); mxs=max(max(k for k,v in n.items() if v>0) for n in N)
    print(f"     самая длинная: факт {mx}, в перемешанном {mxs}")

print("="*78); print("СКОРОГОВОРКА: серии соседних слов, отличающихся не больше чем на один знак"); print("="*78)
report(PARA,"ВОЙНИЧ",close)
sizes=[len(p) for p in PARA]
def chunk(ws):
    o=[];k=0
    for s in sizes:
        if k+s>len(ws): break
        o.append(ws[k:k+s]); k+=s
    return o
lat=open("ref/latin.clean").read().split(); eng=open("ref/english.clean").read().split()
def close_plain(a,b):
    if abs(len(a)-len(b))>1: return False
    if len(a)==len(b): return sum(x!=y for x,y in zip(a,b))<=1
    s,l=(a,b) if len(a)<len(b) else (b,a)
    return any(l[:i]+l[i+1:]==s for i in range(len(l)))
report(chunk(lat),"ЛАТЫНЬ",close_plain)
report(chunk(eng),"АНГЛИЙСКИЙ",close_plain)

print("\n"+"="*78); print("СЛОВАРЬ: серии слов с одинаковым первым знаком (признак сортировки)"); print("="*78)
report(PARA,"ВОЙНИЧ",lambda a,b: gl(a)[0]==gl(b)[0])
report(chunk(lat),"ЛАТЫНЬ",lambda a,b: a[0]==b[0])
report(chunk(eng),"АНГЛИЙСКИЙ",lambda a,b: a[0]==b[0])

print("\n"+"="*78); print("СОРТИРОВКА: растёт ли «алфавитный ранг» первого знака вдоль абзаца"); print("="*78)
freq=collections.Counter(gl(w)[0] for p in PARA for w in p)
rank={g:i for i,(g,_) in enumerate(freq.most_common())}
import math
def spearman(seqs):
    tot=0; n=0
    for s in seqs:
        if len(s)<10: continue
        y=[rank.get(gl(w)[0],0) for w in s]; x=list(range(len(y)))
        mx=sum(x)/len(x); my=sum(y)/len(y)
        num=sum((a-mx)*(b-my) for a,b in zip(x,y))
        den=math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
        if den: tot+=num/den; n+=1
    return tot/n
print(f"  средняя корреляция позиции и ранга первого знака: {spearman(PARA):+.4f}")
print(f"  в перемешанном:                                   {spearman(shuf(PARA,9)):+.4f}")
print("  (у отсортированного списка была бы близка к +1)")
