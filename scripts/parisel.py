# -*- coding: utf-8 -*-
"""Воспроизведение мер Паризеля (arXiv:2604.19762) на RF1b-e и на языках."""
import json, collections, math, random, statistics as st, os, unicodedata, re
def mi(pairs):
    j=collections.Counter(pairs); a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
    n=len(pairs)
    return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
def classes(words, thr=2.0):
    """start-pref / end-pref / ambiguous по порогу 2:1 (доля вхождений в первой позиции против последней)"""
    st_=collections.Counter(); en=collections.Counter()
    for w in words:
        if len(w)<1: continue
        st_[w[0]]+=1; en[w[-1]]+=1
    cls={}
    for g in set(st_)|set(en):
        s,e=st_[g],en[g]
        if e==0 and s==0: continue
        if e==0 or (s and s/max(e,1e-9)>=thr): cls[g]="S"
        elif s==0 or (e and e/max(s,1e-9)>=thr): cls[g]="E"
        else: cls[g]="A"
    return cls, st_, en
def analyse(lines, lab):
    words=[w for l in lines for w in l]
    cls,st_,en=classes(words)
    pairs=[(x[-1],y[0]) for l in lines for x,y in zip(l,l[1:])]
    tot=len(pairs)
    es=sum(1 for a,b in pairs if cls.get(a)=="E" and cls.get(b)=="S")
    M=mi(pairs)
    cp=[(cls.get(a,"?"),cls.get(b,"?")) for a,b in pairs]
    Mc=mi(cp)
    rnd=random.Random(11); sh=0.0
    for _ in range(5):
        f=words[:]; rnd.shuffle(f); i=0; L2=[]
        for l in lines: L2.append(f[i:i+len(l)]); i+=len(l)
        sh+=mi([(x[-1],y[0]) for l in L2 for x,y in zip(l,l[1:])])/5
    n_s=sum(1 for v in cls.values() if v=="S"); n_e=sum(1 for v in cls.values() if v=="E"); n_a=sum(1 for v in cls.values() if v=="A")
    pol=[]
    for g in cls:
        s,e=st_[g],en[g]
        if s+e>0: pol.append(abs(s-e)/(s+e))
    return dict(lab=lab, words=len(words), glyphs=len(cls), S=n_s, E=n_e, A=n_a,
                pol=st.mean(pol) if pol else 0, es=es/max(tot,1), MI=M, MIsh=sh,
                drop=(M-sh)/max(M,1e-9), Mc=Mc, within=1-Mc/max(M,1e-9))
def load_iv(name):
    d=json.load(open(f"data/parsed_{name}.json"))
    L=[[w for w in r["words"] if '?' not in w] for r in d["rows"] if r["locus"]=="P"]
    return [l for l in L if len(l)>=2]
def load_all_loci(name):
    d=json.load(open(f"data/parsed_{name}.json"))
    L=[[w for w in r["words"] if '?' not in w] for r in d["rows"]]
    return [l for l in L if len(l)>=2]
LENS=[len(l) for l in load_iv("ZL3b-n")]
def load_lang(fn):
    w=open(f"ref/{fn}.clean",encoding="utf-8",errors="ignore").read().split()
    out=[];k=0
    for n in LENS:
        if k+n>len(w): break
        out.append(w[k:k+n]); k+=n
    return out
print("="*118); print("ВОСПРОИЗВЕДЕНИЕ ПАРИЗЕЛЯ (arXiv:2604.19762) — его числа в скобках"); print("="*118)
print(f"  {'корпус':>22s} {'слов':>7s} {'знаков':>7s} {'S/E/A':>10s} {'поляриз.':>9s} {'конец→начало':>13s} {'MI':>7s} {'MI перем.':>10s} {'падение':>8s} {'внутрикл.':>10s}")
rows=[("RF1b-e, локус P", load_iv("RF1b-e")), ("RF1b-e, все локусы", load_all_loci("RF1b-e")),
      ("ZL3b, локус P", load_iv("ZL3b-n"))]
for fn,lab in [("english","английский"),("bk_fr1","французский"),("wiki_he","иврит")]:
    if os.path.exists(f"ref/{fn}.clean"): rows.append((lab, load_lang(fn)))
for lab,L in rows:
    r=analyse(L,lab)
    print(f"  {r['lab']:>22s} {r['words']:7d} {r['glyphs']:7d} {r['S']:3d}/{r['E']:2d}/{r['A']:2d} "
          f"{r['pol']:9.3f} {r['es']:12.1%} {r['MI']:7.3f} {r['MIsh']:10.3f} {r['drop']:7.0%} {r['within']:9.0%}")
print()
print("  Паризель на RF1b-e:  37 016 слов; конец→начало 80,6 %; поляризация 0,786;")
print("                       MI 0,223 → 0,049 при перемешивании порядка слов (падение 78 %);")
print("                       внутриклассовая доля MI 97 %.")
print("  Его языки:           англ. 25,7 %, франц. 35,5 %, иврит 28,7 %, араб. 19,8 %;")
print("                       поляризация 0,694–0,860.")
