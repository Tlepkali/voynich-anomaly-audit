# -*- coding: utf-8 -*-
import json, collections, random, statistics as st
D=json.load(open("parsed.json")); PG=D["pages"]
rows=[r for r in D["rows"] if r["locus"]=="P"]
SL="pf"
def clean(r): return [w for w in r["words"] if '?' not in w]
def has(w,gl=SL): return any(g in w for g in gl)
def near(a,b):
    if a==b: return True
    la,lb=len(a),len(b)
    if abs(la-lb)>1: return False
    if la==lb:
        d=0
        for x,y in zip(a,b):
            if x!=y:
                d+=1
                if d>1: return False
        return d==1
    s_,l_=(a,b) if la<lb else (b,a)
    return any(l_[:i]+l_[i+1:]==s_ for i in range(len(l_)))
def perm(lines, gl=SL, B=5000, drop=None):
    tails=[l[1:] for l in lines if len(l)>=3]
    def cnt(tail, flags):
        c=0
        for i in range(len(tail)-1):
            if flags[i] and flags[i+1]:
                if drop and drop(tail[i],tail[i+1]): continue
                c+=1
        return c
    obs=sum(cnt(t,[has(w,gl) for w in t]) for t in tails)
    rnd=random.Random(23); null=[]
    F=[[has(w,gl) for w in t] for t in tails]
    for _ in range(B):
        c=0
        for t,fl in zip(tails,F):
            p=fl[:]; rnd.shuffle(p); c+=cnt(t,p)
        null.append(c)
    null.sort(); m=st.mean(null)
    return obs, m, obs/max(m,.01), (sum(1 for x in null if x>=obs)+1)/(B+1), null[int(.025*B)], null[int(.975*B)]
CONT=lambda r: r["pos"]=="+"
print("="*102); print("ЭФФЕКТ НА СТРОКАХ-ПРОДОЛЖЕНИЯХ: чем он держится"); print("="*102)
print(f"  {'проверка':>46s} {'набл.':>6s} {'ожид.':>7s} {'отн.':>6s} {'95 %':>13s} {'p':>7s}")
ls=[clean(r) for r in rows if CONT(r)]
for lab,gl,dr in [("одноногие p/f — как есть","pf",None),
                  ("  исключены одинаковые соседи","pf",lambda a,b:a==b),
                  ("  исключены соседи на расст. ≤1","pf",near),
                  ("двуногие t/k — контроль","tk",None),
                  ("  двуногие, исключены расст. ≤1","tk",near)]:
    o,m,r_,p,lo,hi=perm(ls,gl,drop=dr)
    print(f"  {lab:>46s} {o:6d} {m:7.1f} {r_:5.2f}× [{lo:4d}; {hi:4d}] {p:7.3f}")
print("\n  То же на ВЕРХНИХ строках абзацев (для сверки):")
lt=[clean(r) for r in rows if r["pos"] in {"@","="}]
for lab,gl,dr in [("одноногие p/f — как есть","pf",None),("  исключены соседи на расст. ≤1","pf",near)]:
    o,m,r_,p,lo,hi=perm(lt,gl,drop=dr)
    print(f"  {lab:>46s} {o:6d} {m:7.1f} {r_:5.2f}× [{lo:4d}; {hi:4d}] {p:7.3f}")
print("\n"+"="*102); print("НЕ ДЕРЖИТСЯ ЛИ ЭФФЕКТ ПРОДОЛЖЕНИЙ НА НЕСКОЛЬКИХ СТРАНИЦАХ"); print("="*102)
byp=collections.defaultdict(list)
for r in rows:
    if CONT(r): byp[r["page"]].append(clean(r))
sc=[]
for pg,lines in byp.items():
    tails=[l[1:] for l in lines if len(l)>=3]
    o=sum(1 for t in tails for i in range(len(t)-1) if has(t[i]) and has(t[i+1]))
    e=sum(sum(1 for w in t if has(w))*(sum(1 for w in t if has(w))-1)/len(t) for t in tails if len(t)>0)
    if o+e>0: sc.append((o,e,pg))
tot_o=sum(o for o,_,_ in sc); tot_e=sum(e for _,e,_ in sc)
pos=sum(1 for o,e,_ in sc if o>e); neg=sum(1 for o,e,_ in sc if o<e)
top=sorted(sc,key=lambda x:-(x[0]-x[1]))[:5]
print(f"  страниц с ненулевым вкладом: {len(sc)};  наблюдено {tot_o}, ожидание {tot_e:.1f}")
print(f"  страниц выше ожидания: {pos}, ниже: {neg}  (знаковый тест: p ≈ {'%.3f'%(2*min(pos,neg)/(pos+neg)) if pos+neg else '—'})")
print(f"  пять главных вкладчиков: "+", ".join(f"{pg} (+{o-e:.1f})" for o,e,pg in top))
print(f"  их доля в общем превышении: {sum(o-e for o,e,_ in top)/max(tot_o-tot_e,.01):.0%}")
