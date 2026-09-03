# -*- coding: utf-8 -*-
import json, collections, statistics as st, math, os, re
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]
LENS=[len(l) for l in VL]
def corr(P):
    xs=[a for a,_ in P]; ys=[b for _,b in P]
    mx,my=st.mean(xs),st.mean(ys)
    n=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
    d=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    return n/d if d else 0
def rank_corr(L):
    f=[w for l in L for w in l]; c=collections.Counter(f)
    rk={w:i+1 for i,(w,_) in enumerate(c.most_common())}
    return corr([(math.log(rk[l[i]]),math.log(rk[l[i+1]])) for l in L for i in range(len(l)-1)])
def relines(flat,lens=None):
    lens=lens or LENS; out=[];k=0
    for n in lens:
        if k+n>len(flat): break
        out.append(flat[k:k+n]); k+=n
    return out
VOW=set("aeiouyаеёиоуыэюяäöüáéíóúàèìòùâêîôûåæø")
def syll(w):
    """грубая слоговая нарезка: разрез между гласной и следующим CV"""
    out=[];cur=""
    i=0
    while i<len(w):
        cur+=w[i]
        if w[i] in VOW:
            j=i+1; cons=0
            while j<len(w) and w[j] not in VOW: cons+=1; j+=1
            if j<len(w) and cons>=1:
                cur+=w[i+1:i+1+cons-1]; out.append(cur); cur=""; i=i+cons
                continue
        i+=1
    if cur:
        if out: out[-1]+=cur
        else: out=[cur]
    return out or [w]
print("="*100); print("ШИРОКИЙ ПРОГОН: корреляция лог-рангов соседних токенов, 34 тыс. слов, строки рукописи"); print("="*100)
rows=[("ВОЙНИЧ", rank_corr(VL), sum(len(l) for l in VL))]
for fn in sorted(os.listdir("ref")):
    if not fn.endswith(".clean"): continue
    w=open("ref/"+fn,encoding="utf-8",errors="ignore").read().split()
    L=relines(w)
    n=sum(len(x) for x in L)
    if n<25000: continue
    rows.append((fn[:-6], rank_corr(L), n))
rows.sort(key=lambda x:x[1])
for nm,r,n in rows:
    mark=" ←" if nm=="ВОЙНИЧ" else ""
    bar="█"*int(abs(r)*80)
    side=" "*(28-min(28,int(abs(r)*80))) if r<0 else ""
    print(f"  {nm:>14s} {r:+7.4f} {n:6d}  {'-'*0}{bar}{mark}")
print("\n"+"="*100); print("ГИПОТЕЗА СЕГМЕНТАЦИИ: что если токены рукописи — не слова, а СЛОГИ"); print("="*100)
print("  беру язык, режу его слова на слоги, считаю ту же меру на слогах как на «словах»")
print(f"\n  {'корпус':>14s} {'слова':>9s} {'СЛОГИ':>9s} {'ср.длина слога':>15s} {'знак меняется':>14s}")
for fn in ["latin","english","wiki_de","wiki_it","wiki_fi","wiki_tr"]:
    p="ref/%s.clean"%fn
    if not os.path.exists(p): continue
    w=open(p,encoding="utf-8",errors="ignore").read().split()[:40000]
    a=rank_corr(relines(w))
    sy=[s for x in w for s in syll(x)]
    b=rank_corr(relines(sy))
    ml=st.mean(len(s) for s in sy)
    ch="ДА" if (a<0)!=(b<0) else "нет"
    print(f"  {fn:>14s} {a:+9.4f} {b:+9.4f} {ml:15.2f} {ch:>14s}")
print(f"\n  для сравнения: Войнич {rank_corr(VL):+.4f} при средней длине токена "
      f"{st.mean(len(w) for l in VL for w in l):.2f}")
