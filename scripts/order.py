# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os, sys, math
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]
LENS=[len(l) for l in VL]; N=sum(LENS)
VOY=[w for l in VL for w in l]
def cut(flat):
    out=[];k=0
    for n in LENS:
        if k+n>len(flat): break
        out.append(flat[k:k+n]); k+=n
    return out
def load(fn,n=N):
    p="ref/%s.clean"%fn
    if not os.path.exists(p): return None
    w=open(p).read().split()
    return w[:n] if len(w)>=n else None
def wshuf(flat,W,seed):
    rnd=random.Random(seed); out=flat[:]
    for i in range(0,len(out),W):
        blk=out[i:i+W]; rnd.shuffle(blk); out[i:i+W]=blk
    return out
def rep_bigram(flat):
    L=cut(flat)
    big=collections.Counter((l[i],l[i+1]) for l in L for i in range(len(l)-1))
    tok=sum(big.values())
    return sum(v for v in big.values() if v>=2)/tok, len(big)/tok
BUCK=None
def buckets(flat,k=5):
    c=collections.Counter(flat); order=[w for w,_ in c.most_common()]
    cut_=[10,50,200,1000]
    b={}
    for i,w in enumerate(order):
        j=0
        while j<len(cut_) and i>=cut_[j]: j+=1
        b[w]=j
    return b
def class_mi(flat,b):
    L=cut(flat)
    pairs=[(b[l[i]],b[l[i+1]]) for l in L for i in range(len(l)-1)]
    j=collections.Counter(pairs); n=len(pairs)
    pa=collections.Counter(x for x,_ in pairs); pb=collections.Counter(y for _,y in pairs)
    return sum(c/n*math.log2((c/n)/((pa[x]/n)*(pb[y]/n))) for (x,y),c in j.items())
CORP=[("Войнич",VOY)]
for nm,fn in [("латынь","latin"),("английский","english"),("итальянский","wiki_it")]:
    w=load(fn)
    if w: CORP.append((nm,w))
sys.path.insert(0,"scripts"); sys.path.insert(0,".")
try:
    exec(open("scripts/oos.py").read().split("CORP=")[0])
    M=model()
    if M: CORP.append(("МОДЕЛЬ",[w for l in M for w in l][:N]))
except Exception as e: print("модель не собралась:",e)
print("="*118); print("ЕСТЬ ЛИ ПОРЯДОК СЛОВ: повторяющиеся биграммы против перемешивания ВНУТРИ ОКНА"); print("="*118)
print("  окно сохраняет местный состав словаря (тему) и разрушает только порядок")
print(f"\n  {'корпус':>14s} {'слов':>6s} {'набл.':>7s} | "+" ".join(f"{'окно '+str(W):>13s}" for W in (5,10,25,50)))
for nm,flat in CORP:
    o,_=rep_bigram(flat); cells=[]
    for W in (5,10,25,50):
        v=[rep_bigram(wshuf(flat,W,s))[0] for s in range(6)]
        m=st.mean(v); cells.append(f"{m:.3f} ({o/max(m,1e-9):.2f}×)")
    print(f"  {nm:>14s} {len(flat):6d} {o:7.3f} | "+" ".join(f"{c:>13s}" for c in cells))
print("\n"+"="*118); print("ВЗАИМНАЯ ИНФОРМАЦИЯ КЛАССОВ ЧАСТОТЫ (5 корзин: топ-10, 11–50, 51–200, 201–1000, прочие)"); print("="*118)
print("  оценивается по 25 ячейкам на 34 тыс. пар — разреженности нет")
print(f"\n  {'корпус':>14s} {'набл.':>7s} | "+" ".join(f"{'окно '+str(W):>14s}" for W in (5,10,25,50)))
for nm,flat in CORP:
    b=buckets(flat); o=class_mi(flat,b); cells=[]
    for W in (5,10,25,50):
        v=[class_mi(wshuf(flat,W,s),b) for s in range(6)]
        m=st.mean(v); cells.append(f"{m:.4f} ({o/max(m,1e-9):.1f}×)")
    print(f"  {nm:>14s} {o:7.4f} | "+" ".join(f"{c:>14s}" for c in cells))
