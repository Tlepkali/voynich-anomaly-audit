# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, os
D=json.load(open("parsed.json"))
VL=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
VOY=[w for l in VL for w in l]
MULTI=["cth","cph","ckh","cfh","ch","sh","ee"]
CORE=set("tpkf")|{"cth","cph","ckh","cfh"}
MANTLE={"ch","sh","ee"}
CRUST=set("dlrsnxrmg")
def toks(w):
    out=[];i=0
    while i<len(w):
        for m in MULTI:
            if w.startswith(m,i): out.append(m); i+=len(m); break
        else: out.append(w[i]); i+=1
    return out
def cls(t): return 3 if t in CORE else (2 if t in MANTLE else (1 if t in CRUST else 0))
def nested(w):
    c=[cls(t) for t in toks(w) if cls(t)>0]
    if len(c)<2: return None                 # нечего проверять
    top=max(c); k=c.index(top)
    return all(c[i]<=c[i+1] for i in range(k)) and all(c[i]>=c[i+1] for i in range(k,len(c)-1))
def rate(types, shuffle=False, seed=0):
    rnd=random.Random(seed); ok=0; n=0
    for w in types:
        if shuffle:
            t=toks(w); rnd.shuffle(t); w="".join(t)
        r=nested(w)
        if r is not None: n+=1; ok+=r
    return ok/max(n,1), n
print("="*100); print("СХЕМА СТОЛЬФИ: вложены ли слои crust → mantle → core → mantle → crust"); print("="*100)
print("  классы по Стольфи: ядро t p k f cth cph ckh cfh | мантия ch sh ee | кора d l r s n x m g")
print("  контроль: перемешивание ЗНАКОВ ВНУТРИ СЛОВА (состав тот же, порядок случайный)\n")
T=sorted(set(VOY))
o,n=rate(T)
sh=[rate(T,True,s)[0] for s in range(20)]
print(f"  {'выборка':>26s} {'типов с ≥2 класс.':>18s} {'вложено':>9s} {'при перемешивании':>19s} {'отношение':>10s}")
print(f"  {'Войнич, типы':>26s} {n:18,d} {o:9.1%} {st.mean(sh):18.1%} {o/st.mean(sh):9.2f}×")
tok_o=0; tok_n=0
for w in VOY:
    r=nested(w)
    if r is not None: tok_n+=1; tok_o+=r
print(f"  {'Войнич, токены':>26s} {tok_n:18,d} {tok_o/tok_n:9.1%} {'':>18s} {'':>9s}")
print(f"\n  разброс контроля по 20 зёрнам: {min(sh):.1%}–{max(sh):.1%}")
print("\n"+"="*100); print("ТА ЖЕ ПРОВЕРКА НА ЯЗЫКАХ И НА МОДЕЛИ (те же классы знаков — проверка на бессмысленность меры)"); print("="*100)
print(f"  {'корпус':>26s} {'типов':>10s} {'вложено':>9s} {'перемеш.':>10s} {'отношение':>10s}")
import sys
sys.path.insert(0,"scripts")
for nm,fn in [("латынь","latin"),("английский","english"),("немецкий","wiki_de"),("итальянский","wiki_it")]:
    p="ref/%s.clean"%fn
    if not os.path.exists(p): continue
    ws=sorted(set(open(p).read().split()[:60000]))
    o2,n2=rate(ws); s2=st.mean(rate(ws,True,s)[0] for s in range(5))
    print(f"  {nm:>26s} {n2:10,d} {o2:9.1%} {s2:10.1%} {o2/max(s2,1e-9):9.2f}×")
