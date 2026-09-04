# -*- coding: utf-8 -*-
"""СИСТЕМА КРИВОЙ И ЛИНИИ (Брайан Чам, 2014). Глифы делятся на кривые [c],
линейные [l], гибрид [a] и прозрачные [E] (виселицы, невидимы для правила).
Правило «подобное к подобному»: допустимо ccc, lll, ccall; недопустимо cl, lc, la.
То есть последовательность после удаления прозрачных должна ложиться в
c* a? l*, причём переход от кривых к линейным ТОЛЬКО через a.
Заявлено: 71,49 % слов в базовой системе, 96,63 % с двумя заплатами.
Заплата 1: ol, or, ar, al — отдельные КРИВЫЕ глифы. Заплата 2: l и r как
необязательные приставки в начале слова.

Нуля в поле для этого нет, как и для слотов Заттеры. Ставлю.
"""
import sys, collections, random
sys.path.insert(0,"scripts")
import measures as M

CURVE={"o","e","ee","eee","y","ch","sh","d","q"}
LINE ={"i","ii","iii","r","s","l","m","n"}
HYB  ={"a"}
TRANS={"t","k","p","f","cth","ckh","cph","cfh","g","x","v","j","u","z","b","h"}
MULTI=["eee","cth","ckh","cph","cfh","iii","ch","sh","ee","ii"]
def toks(w):
    out=[];i=0
    while i<len(w):
        for m in MULTI:
            if w.startswith(m,i): out.append(m); i+=len(m); break
        else: out.append(w[i]); i+=1
    return out
def cls_of(g):
    if g in CURVE: return "c"
    if g in LINE:  return "l"
    if g in HYB:   return "a"
    return "E"
def conform(w, patch1=False, patch2=False):
    t=toks(w)
    if patch2:
        while t and t[0] in ("l","r"): t=t[1:]     # l и r как приставки
    if patch1:
        out=[];i=0
        while i<len(t):
            if i+1<len(t) and t[i] in ("o","a") and t[i+1] in ("l","r"):
                out.append("§"); i+=2               # ol, or, ar, al — одна кривая
            else: out.append(t[i]); i+=1
        t=out
    seq="".join("c" if x=="§" else cls_of(x) for x in t)
    seq=seq.replace("E","")
    if not seq: return True
    i=0
    while i<len(seq) and seq[i]=="c": i+=1
    had_a=False
    if i<len(seq) and seq[i]=="a": had_a=True; i+=1
    j=i
    while j<len(seq) and seq[j]=="l": j+=1
    if j!=len(seq): return False
    has_c=i>0 if not had_a else i>1
    has_l=j>i
    if has_c and has_l and not had_a: return False
    return True

VL=M.load(); toks_all=M.tokens(VL); T=M.types(VL)
cnt=collections.Counter(toks_all)
print("="*96); print("СИСТЕМА КРИВОЙ И ЛИНИИ: ПОКРЫТИЕ"); print("="*96)
for p1,p2,lab in [(False,False,"базовая система"),(True,False,"+ заплата 1 (ol, or, ar, al)"),
                  (True,True,"+ обе заплаты")]:
    ok_t=[w for w in T if conform(w,p1,p2)]
    nt=sum(cnt[w] for w in ok_t)
    print(f"  {lab:>30s}: типов {len(ok_t)/len(T):6.1%}, ТОКЕНОВ {nt/len(toks_all):6.1%}")
print(f"\n  ЗАЯВЛЕНО ЧАМОМ: 71,49 % базовая, 96,63 % с двумя заплатами")
print("\n"+"="*96); print("НУЛЬ, КОТОРОГО В ПОЛЕ НЕТ"); print("="*96)
rnd=random.Random(5); mp={w:"".join(rnd.sample(w,len(w))) for w in T}
for p1,p2,lab in [(False,False,"базовая"),(True,True,"с заплатами")]:
    real=sum(1 for w in T if conform(w,p1,p2))/len(T)
    shuf=sum(1 for w in T if conform(mp[w],p1,p2))/len(T)
    print(f"  {lab:>14s}: рукопись {real:6.1%}, перемешка знаков в слове {shuf:6.1%}, отношение {real/max(shuf,1e-9):5.1f}×")
