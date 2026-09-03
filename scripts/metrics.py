import math, collections

MULTI = ["cfhaiin","ckhaiin","cthaiin","cphaiin","cfh","ckh","cth","cph","sh","ch",
         "iiin","iin","ii","eee","ee","aiin","ain","aiir","air","qo","dy"]
def merge(w):
    out,i=[],0
    while i<len(w):
        for m in MULTI:
            if w.startswith(m,i): out.append(m); i+=len(m); break
        else: out.append(w[i]); i+=1
    return out

def _h(units):
    uni=collections.Counter(units); T=len(units)
    h1=-sum(n/T*math.log2(n/T) for n in uni.values())
    bi=collections.Counter(zip(units,units[1:])); M=sum(bi.values())
    h2=-sum(n/M*math.log2(n/M) for n in bi.values())-h1
    return h1,h2

def _posclass(n,i): return "1" if n==1 else ("b" if i==0 else ("e" if i==n-1 else "m"))
def _mi(seqs):
    j=collections.Counter()
    for u in seqs:
        for i,c in enumerate(u): j[(c,_posclass(len(u),i))]+=1
    T=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (g,p),n in j.items(): pg[g]+=n; pp[p]+=n
    return sum(n/T*math.log2((n/T)/((pg[g]/T)*(pp[p]/T))) for (g,p),n in j.items())

def _ed1(a,b):
    if a==b or abs(len(a)-len(b))>1: return False
    if len(a)==len(b): return sum(x!=y for x,y in zip(a,b))==1
    s,l=(a,b) if len(a)<len(b) else (b,a)
    return any(l[:i]+l[i+1:]==s for i in range(len(l)))

def _zipf(freqs):
    """наклон log-log регрессии частота ~ ранг по первым 1000 рангам"""
    f=sorted(freqs, reverse=True)[:1000]
    xs=[math.log(i+1) for i in range(len(f))]; ys=[math.log(v) for v in f]
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)

def all_metrics(words, lines=None):
    """lines — список списков слов, если структура строк есть; иначе None"""
    chars=[]; 
    for w in words: chars.extend(list(w)); chars.append(" ")
    h1,h2=_h(chars)
    mch=[]
    for w in words: mch.extend(merge(w)); mch.append(" ")
    _,h2m=_h(mch)
    ln=[len(w) for w in words]; mu=sum(ln)/len(ln)
    sd=(sum((l-mu)**2 for l in ln)/len(ln))**0.5
    ty=collections.Counter(words); T=len(words)
    same=sum(1 for a,b in zip(words,words[1:]) if a==b)
    exp=sum((n/T)**2 for n in ty.values())*(T-1)
    ed1=sum(1 for a,b in zip(words,words[1:]) if _ed1(a,b))/(T-1)
    wh1,wh2=_h(words)
    m=dict(mean_len=mu, cv=sd/mu, h1=h1, h2=h2, h2_merged=h2m,
           mi_pos=_mi([list(w) for w in words]), mi_pos_merged=_mi([merge(w) for w in words]),
           rep_ratio=same/exp if exp else 0, ed1=ed1,
           ttr=len(ty)/T, hapax=sum(1 for v in ty.values() if v==1)/len(ty),
           wh2=wh2, zipf=_zipf(list(ty.values())))
    if lines:
        fi=collections.Counter(l[0][0] for l in lines if l)
        re_=collections.Counter(w[0] for l in lines for w in l[1:])
        Tf=sum(fi.values()); Tr=sum(re_.values())
        # расхождение распределений первых букв: начало строки против прочих
        keys=set(fi)|set(re_)
        m['line_div']=0.5*sum(abs(fi.get(k,0)/Tf - re_.get(k,0)/Tr) for k in keys)
    return m
