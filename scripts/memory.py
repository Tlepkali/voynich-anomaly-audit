# -*- coding: utf-8 -*-
"""Какая минимальная память в порождении закрывает разрыв с рукописью.
УСЛОВИЯ ЗАДАНЫ ДО ЗАПУСКА:
  подгоняется — профиль возврата слова (recurrence);
  отложено и не настраивается — соседство одинаковых, автокорреляция длины,
  ранг-корреляция соседей, стык по 1 знаку.
"""
import json, collections, random, statistics as st, math
def load(n="ZL3b-n"):
    d=json.load(open(f"data/parsed_{n}.json"))
    L=[[w for w in r["words"] if '?' not in w] for r in d["rows"] if r["locus"]=="P"]
    return [l for l in L if len(l)>=3]
VL=load(); LENS=[len(l) for l in VL]; VOY=[w for l in VL for w in l]
def cut(flat):
    out=[];k=0
    for n in LENS:
        if k+n>len(flat): break
        out.append(flat[k:k+n]); k+=n
    return out
# ---- меры ----
def recurrence(L, maxd=60):
    """во сколько раз чаще слово возвращается на расстоянии d, чем при перемешивании"""
    f=[w for l in L for w in l]
    pos=collections.defaultdict(list)
    for i,w in enumerate(f): pos[w].append(i)
    obs=collections.Counter()
    for v in pos.values():
        for a,b in zip(v,v[1:]):
            if b-a<=maxd: obs[b-a]+=1
    rnd=random.Random(5); exp=collections.Counter()
    for _ in range(3):
        g=f[:]; rnd.shuffle(g); p2=collections.defaultdict(list)
        for i,w in enumerate(g): p2[w].append(i)
        for v in p2.values():
            for a,b in zip(v,v[1:]):
                if b-a<=maxd: exp[b-a]+=1/3
    return {d:(obs[d]/exp[d] if exp[d]>0.5 else float('nan')) for d in range(1,maxd+1)}
def prof_summary(r):
    """три числа: превышение на d=1..5, на 6..20, расстояние выхода на 1,0"""
    a=st.mean(r[d] for d in range(1,6) if r[d]==r[d])
    b=st.mean(r[d] for d in range(6,21) if r[d]==r[d])
    tail=[d for d in range(5,61) if r.get(d,float('nan'))==r.get(d,float('nan')) and r[d]<1.05]
    return a,b,(tail[0] if tail else 60)
def adj_ident(L,B=6,seed=3):
    o=sum(1 for l in L for i in range(len(l)-1) if l[i]==l[i+1])
    rnd=random.Random(seed); acc=0.0
    for _ in range(B):
        for l in L:
            p=rnd.sample(l,len(l)); acc+=sum(1 for a,b in zip(p,p[1:]) if a==b)/B
    return o/max(acc,.01)
def len_autocorr(L,d=1):
    xs=[];ys=[]
    for l in L:
        for i in range(len(l)-d): xs.append(len(l[i])); ys.append(len(l[i+d]))
    mx,my=st.mean(xs),st.mean(ys)
    n=sum((a-mx)*(b-my) for a,b in zip(xs,ys)); dn=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    return n/dn if dn else 0
def rank_corr(L):
    f=[w for l in L for w in l]; c=collections.Counter(f)
    rk={w:i+1 for i,(w,_) in enumerate(c.most_common())}
    xs=[];ys=[]
    for l in L:
        for i in range(len(l)-1): xs.append(math.log(rk[l[i]])); ys.append(math.log(rk[l[i+1]]))
    mx,my=st.mean(xs),st.mean(ys)
    n=sum((a-mx)*(b-my) for a,b in zip(xs,ys)); dn=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    return n/dn if dn else 0
def mi(pairs):
    j=collections.Counter(pairs); a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
    n=len(pairs); return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
def junc1(L,seed=9):
    pr=lambda LL:[(x[-1:],y[:1]) for l in LL for x,y in zip(l,l[1:])]
    o=mi(pr(L)); f=[w for l in L for w in l]; rnd=random.Random(seed); s=0.0
    for _ in range(3):
        sh=f[:]; rnd.shuffle(sh); s+=mi(pr(cut(sh)))/3
    return o-s
# ---- порождающие модели ----
def memoryless(seed=0):
    rnd=random.Random(seed); f=VOY[:]; rnd.shuffle(f); return cut(f)
def cache(p, w, seed=0):
    """с вероятностью p повторяем слово из последних w, иначе берём из общего мешка"""
    rnd=random.Random(seed); bag=VOY[:]; rnd.shuffle(bag)
    out=[]; recent=collections.deque(maxlen=w); i=0
    while i<len(VOY):
        if recent and rnd.random()<p: x=recent[rnd.randrange(len(recent))]
        else:
            x=bag[i]; i+=1
        out.append(x); recent.append(x)
        if i>=len(bag): break
    return cut(out[:len(VOY)])
def battery(L, lab):
    r=recurrence(L); a,b,t=prof_summary(r)
    return dict(lab=lab, r1=a, r2=b, tail=t, adj=adj_ident(L), la=len_autocorr(L),
                rc=rank_corr(L), j=junc1(L))
print("="*112); print("ЧТО ТЕРЯЕТ БЕЗПАМЯТНОЕ ПОРОЖДЕНИЕ"); print("="*112)
print(f"  {'модель':>30s} {'возврат d1-5':>13s} {'d6-20':>8s} {'выход':>7s} | "
      f"{'соседство':>10s} {'автокорр':>9s} {'ранг-корр':>10s} {'стык':>7s}")
rows=[battery(VL,"РУКОПИСЬ"), battery(memoryless(0),"безпамятное (перемешка)")]
for d in rows:
    print(f"  {d['lab']:>30s} {d['r1']:13.2f} {d['r2']:8.2f} {d['tail']:6d}  | "
          f"{d['adj']:9.2f}× {d['la']:+9.3f} {d['rc']:+10.4f} {d['j']:7.3f}")
print("\n  ПОДГОНКА ведётся ТОЛЬКО по трём левым столбцам. Четыре правых отложены.")
