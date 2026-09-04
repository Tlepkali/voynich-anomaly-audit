# -*- coding: utf-8 -*-
"""ТРИ ОПУБЛИКОВАННЫЕ МОДЕЛИ УСТРОЙСТВА СЛОВА ПОД ОДНИМ НУЛЁМ.
Нуль один и тот же для всех: перемешивание ГЛИФОВ ВНУТРИ СЛОВА (сохраняет
набор глифов и длину, разрушает порядок), на типах.

  1. Стольфи, «ядро-мантия-кора»: последовательность классов унимодальна.
  2. Чам 2014, кривая-линия: c* a? l*, переход только через a.
  3. Заттера 2022, 12 слотов: глифы в неубывающем порядке слотов.

В записи A1 нуль был ДРУГОЙ (перемешивались КЛАССЫ, не глифы), поэтому её
1,09× с остальными несравним. Здесь всё на одном нуле.
"""
import sys, collections, random
sys.path.insert(0,"scripts")
import measures as M

MULTI=["eee","cth","ckh","cph","cfh","iii","ch","sh","ee","ii"]
def toks(w):
    out=[];i=0
    while i<len(w):
        for m in MULTI:
            if w.startswith(m,i): out.append(m); i+=len(m); break
        else: out.append(w[i]); i+=1
    return out

# 1. Стольфи
CORE=set("tpkf")|{"cth","cph","ckh","cfh"}; MANTLE={"ch","sh","ee","eee"}; CRUST=set("dlrsnxmg")
def stolfi(w):
    c=[3 if t in CORE else (2 if t in MANTLE else (1 if t in CRUST else 0)) for t in toks(w)]
    c=[x for x in c if x>0]
    if len(c)<2: return True
    k=c.index(max(c))
    return all(c[i]<=c[i+1] for i in range(k)) and all(c[i]>=c[i+1] for i in range(k,len(c)-1))
# 2. Чам
CURVE={"o","e","ee","eee","y","ch","sh","d","q"}; LINE={"i","ii","iii","r","s","l","m","n"}
def cham(w, patch=True):
    t=toks(w)
    if patch:
        while t and t[0] in ("l","r"): t=t[1:]
        out=[];i=0
        while i<len(t):
            if i+1<len(t) and t[i] in ("o","a") and t[i+1] in ("l","r"): out.append("§"); i+=2
            else: out.append(t[i]); i+=1
        t=out
    seq="".join("c" if x=="§" else ("c" if x in CURVE else ("l" if x in LINE else ("a" if x=="a" else "E"))) for x in t).replace("E","")
    if not seq: return True
    i=0
    while i<len(seq) and seq[i]=="c": i+=1
    had=False
    if i<len(seq) and seq[i]=="a": had=True; i+=1
    j=i
    while j<len(seq) and seq[j]=="l": j+=1
    if j!=len(seq): return False
    return not (i>(1 if had else 0) and j>i and not had)
# 3. Заттера
SLOT={0:{"q","s","d"},1:{"o","y"},2:{"l","r"},3:{"t","p","k","f"},4:{"ch","sh"},
      5:{"cth","cph","ckh","cfh"},6:{"e","ee","eee"},7:{"d","s"},8:{"a","o"},
      9:{"i","ii","iii"},10:{"d","l","m","n","r"},11:{"y"}}
G2=collections.defaultdict(set)
for k,v in SLOT.items():
    for g in v: G2[g].add(k)
GL=sorted(G2, key=lambda x:-len(x))
def zattera(w):
    memo={}
    def go(i, lo):
        if i==len(w): return True
        if (i,lo) in memo: return memo[(i,lo)]
        ok=False
        for g in GL:
            if w.startswith(g,i):
                for s in sorted(G2[g]):
                    if s>=lo and go(i+len(g), s): ok=True; break
            if ok: break
        memo[(i,lo)]=ok; return ok
    return go(0,0)

T=M.types(M.load())
rnd=random.Random(5); SH={w:"".join(rnd.sample(w,len(w))) for w in T}
print("="*96); print("ТРИ МОДЕЛИ ПОД ОДНИМ НУЛЁМ (перемешивание глифов в слове, типы)"); print("="*96)
print(f"  {'модель':>34s} {'рукопись':>10s} {'перемешка':>11s} {'отношение':>10s}")
for lab,fn in [("Стольфи: ядро-мантия-кора", stolfi),
               ("Чам 2014: кривая-линия (с заплатами)", cham),
               ("Заттера 2022: 12 слотов", zattera)]:
    a=sum(1 for w in T if fn(w))/len(T)
    b=sum(1 for w in T if fn(SH[w]))/len(T)
    print(f"  {lab:>34s} {a:10.1%} {b:11.1%} {a/max(b,1e-9):9.1f}×")
print("\n  порядок один и тот же при любом зерне перемешки; проверено на 5 зёрнах:")
for lab,fn in [("Стольфи", stolfi),("Чам", cham),("Заттера", zattera)]:
    rs=[]
    for s in range(5):
        r=random.Random(100+s); sh={w:"".join(r.sample(w,len(w))) for w in T}
        a=sum(1 for w in T if fn(w))/len(T); b=sum(1 for w in T if fn(sh[w]))/len(T)
        rs.append(a/max(b,1e-9))
    print(f"    {lab:>10s}: {min(rs):.1f}–{max(rs):.1f}×")
