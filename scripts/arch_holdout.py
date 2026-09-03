# -*- coding: utf-8 -*-
"""Четвёртая архитектура против мер, под которые она НЕ настраивалась.
Настроена была под четыре: возврат, автокорреляция длины, ранг-корреляция, стык.
Всё остальное ниже — отложено по построению."""
import json, collections, random, statistics as st, math
exec(open("scripts/construct5.py").read().split('print("="*100)')[0])
BEST=(0.15,0.10,0.20)
GEN=[arch5(*BEST,seed=s) for s in range(3)]
def flat(L): return [w for l in L for w in l]
def types(L): return sorted({w for l in L for w in l})
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
    T=set(T); nb=nbrs(T)
    m=st.mean(len(nb.get(w,())) for w in T)
    def at(d):
        g=[len(nb.get(w,())) for w in T if len(w)==d]
        return st.mean(g) if len(g)>=15 else float('nan')
    a,b=at(3),at(5)
    return m,(b/a if a==a and b==b and a>0 else float('nan'))
def mi(pairs):
    j=collections.Counter(pairs); a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
    n=len(pairs); return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
def junc(L,k,seed=9):
    pr=lambda LL:[(x[-k:],y[:k]) for l in LL for x,y in zip(l,l[1:])]
    o=mi(pr(L)); f=flat(L); rnd=random.Random(seed); s=0.0
    for _ in range(3):
        sh=f[:]; rnd.shuffle(sh); i=0; SH=[]
        for l in L: SH.append(sh[i:i+len(l)]); i+=len(l)
        s+=mi(pr(SH))/3
    return o-s
def markov_regen(T, order=2, seed=0):
    rnd=random.Random(seed); tr=collections.defaultdict(collections.Counter)
    for w in T:
        s="^"*order+w+"$"
        for i in range(order,len(s)): tr[s[i-order:i]][s[i]]+=1
    pools={k:[c for c,n in v.items() for _ in range(n)] for k,v in tr.items()}
    want=collections.Counter(len(w) for w in T); got=collections.Counter(); out=set(); g=0
    while len(out)<len(T) and g<len(T)*200:
        g+=1; ctx="^"*order; w=""
        while True:
            p=pools.get(ctx)
            if not p: break
            c=p[rnd.randrange(len(p))]
            if c=="$": break
            w+=c; ctx=(ctx+c)[-order:]
            if len(w)>25: break
        if not w or w in out or got[len(w)]>=want.get(len(w),0): continue
        out.add(w); got[len(w)]+=1
    return len(set(out)&set(T))/max(len(out),1)
def zipf(freqs):
    f=sorted(freqs,reverse=True)[:1000]
    xs=[math.log(i+1) for i in range(len(f))]; ys=[math.log(v) for v in f]
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)
def line_div(L):
    fi=collections.Counter(l[0][0] for l in L if l)
    mid=collections.Counter(w[0] for l in L for w in l[1:])
    a=sum(fi.values()); b=sum(mid.values())
    return sum(abs(fi[c]/a - mid[c]/b) for c in set(fi)|set(mid))/2
def profile(L):
    f=flat(L); T=types(L); c=collections.Counter(f)
    m,sh=dens(T)
    return dict(ttr=len(T)/len(f), hap=sum(1 for v in c.values() if v==1)/len(T),
                ml=st.mean(len(w) for w in f), zipf=zipf(c.values()),
                dens=m, shape=sh, j1=junc(L,1), j3=junc(L,3),
                regen=markov_regen(T), ldiv=line_div(L))
print("="*104); print("ЧЕТВЁРТАЯ АРХИТЕКТУРА ПРОТИВ ОТЛОЖЕННЫХ МЕР"); print("="*104)
V=profile(VL)
Gs=[profile(g) for g in GEN]
G={k:(st.mean(d[k] for d in Gs), st.stdev(d[k] for d in Gs)) for k in V}
print(f"  {'мера':>28s} {'рукопись':>10s} {'модель':>16s} {'доля':>8s} {'настраивалась?':>15s}")
rows=[("TTR","ttr","%.3f",0),("доля хапаксов","hap","%.3f",0),("средняя длина слова","ml","%.2f",0),
      ("наклон Ципфа","zipf","%.3f",0),("плотность окрестности","dens","%.2f",0),
      ("профиль плотности дл5/дл3","shape","%.2f",0),("стык по 1 знаку","j1","%.3f",1),
      ("стык по 3 знакам","j3","%.3f",0),("порождение цепью","regen","%.3f",0),
      ("расхождение начала строки","ldiv","%.3f",0)]
for nm,k,fmt,fit in rows:
    v=V[k]; g,sd=G[k]
    r=g/v if v else float('nan')
    print(f"  {nm:>28s} {fmt%v:>10s} {fmt%g:>10s}±{sd:5.3f} {r:7.0%} {'ДА':>15s}" if fit else
          f"  {nm:>28s} {fmt%v:>10s} {fmt%g:>10s}±{sd:5.3f} {r:7.0%} {'отложена':>15s}")
ok=sum(1 for nm,k,_,fit in rows if not fit and 0.7<=G[k][0]/V[k]<=1.43)
tot=sum(1 for _,_,_,fit in rows if not fit)
print(f"\n  отложенных мер в пределах ±43 % от цели: {ok} из {tot}")
