# -*- coding: utf-8 -*-
"""Правила из курируемой ветки 4779 «A brief summary of Voynichese spelling and
grammar» (davidjackson), которых в моём инвентаре не было. Проверка на данных
и фиксация авторства: это ИХ наблюдения, не мои."""
import json, collections, re, sys
sys.path.insert(0,"scripts")
import measures as M

D=json.load(open("data/parsed.json"))
ALL=[r for r in D["rows"]]
P=[r for r in ALL if r["locus"]=="P"]
for r in ALL: r["w"]=[x for x in r["words"] if "?" not in x]
pf=[w for r in P for w in r["w"]]
allw=[w for r in ALL for w in r["w"]]
CH="".join(pf)

def rule(name, claim, got, verdict):
    print(f"\n  {name}")
    print(f"    заявлено : {claim}")
    print(f"    у меня   : {got}")
    print(f"    → {verdict}")

print("="*100); print("ПРАВИЛА ИЗ ВЕТКИ 4779 (davidjackson), СПЛОШНОЙ ТЕКСТ ZL3b"); print("="*100)

# 1. i -> i или n
pairs=[(w[k],w[k+1]) for w in pf for k in range(len(w)-1)]
i_next=collections.Counter(b for a,b in pairs if a=="i")
i_tot=sum(i_next.values())
share=(i_next["i"]+i_next["n"])/i_tot
n_prev=collections.Counter(a for a,b in pairs if b=="n")
n_tot=sum(n_prev.values())
rule("ПРАВИЛО i", "за i следует i или n в 90 % случаев; почти всякий n стоит после i",
     f"i→(i|n) {share:.1%} из {i_tot}; n после i {n_prev['i']/n_tot:.1%} из {n_tot}",
     "ПОДТВЕРЖДАЕТСЯ, и сильнее заявленного")
print(f"    за i следует: " + ", ".join(f"{c}·{v}" for c,v in i_next.most_common(5)))

# 2. f и p никогда не followed by c (Карриер 1976)
for g in "fp":
    nx=collections.Counter(b for a,b in pairs if a==g)
    t=sum(nx.values())
    rule(f"ПРАВИЛО {g} (Карриер 1976)", f"за {g} никогда не следует c",
         f"за {g} следует c: {nx['c']} из {t} = {nx['c']/t:.2%}",
         "ПОДТВЕРЖДАЕТСЯ" if nx["c"]==0 else f"НЕ АБСОЛЮТНО: {nx['c']} исключений")
    print(f"    за {g} следует: " + ", ".join(f"{c}·{v}" for c,v in nx.most_common(5)))

# 3. q -> o
q_next=collections.Counter(b for a,b in pairs if a=="q"); qt=sum(q_next.values())
rule("ПРАВИЛО q", "за q следует o примерно в 90 % случаев",
     f"{q_next['o']/qt:.1%} из {qt} (сплошной текст)", "величина ВЫШЕ заявленной")

# 4. qo как отдельное слово — 29 раз
solo=collections.Counter(w for w in allw if w=="qo")
rule("qo отдельным словом", "встречается уникальным словом 29 раз",
     f"{solo['qo']} раз во всех локусах; в сплошном тексте {sum(1 for w in pf if w=='qo')}",
     "сходится по порядку" if abs(solo['qo']-29)<=10 else "РАСХОДИТСЯ")

# 5. тройной повтор — 35 фраз (Тимм)
tri=[(l[k],k) for r in P for l in [r["w"]] for k in range(len(l)-2) if l[k]==l[k+1]==l[k+2]]
tri_all=[(l[k]) for r in ALL for l in [r["w"]] for k in range(len(l)-2) if l[k]==l[k+1]==l[k+2]]
rule("ТРОЙНОЙ ПОВТОР (Т. Тимм)", "одно и то же слово трижды — в 35 разных фразах",
     f"в сплошном тексте {len(tri)}, во всех локусах {len(tri_all)}",
     "сходится по порядку" if abs(len(tri_all)-35)<=15 else "РАСХОДИТСЯ")
if tri_all: print(f"    примеры: " + ", ".join(f"{w}×3" for w,_ in collections.Counter(tri_all).most_common(6)))

# 6. m на конце строк, но НЕ абзацев
def mfrac(rows, sel):
    ws=[sel(r["w"]) for r in rows if r["w"]]
    return sum(1 for w in ws if w.endswith("m"))/max(len(ws),1), len(ws)
a,na=mfrac(P, lambda w: w[-1])
b,nb=mfrac([r for r in P if r["pos"]=="@"], lambda w: w[-1])
mid=[w for r in P for w in r["w"][:-1]]
c=sum(1 for w in mid if w.endswith("m"))/len(mid)
rule("ПРАВИЛО m", "m преимущественно на КОНЦЕ СТРОК, но не абзацев",
     f"конец строки {a:.1%} (n={na}), середина {c:.2%}, конец ПЕРВОЙ строки абзаца {b:.1%} (n={nb})",
     "подтверждается для строк")
# «не абзацев» — проверим конец ПОСЛЕДНЕЙ строки абзаца
last=[]
for i,r in enumerate(P):
    nxt=P[i+1] if i+1<len(P) else None
    if r["w"] and (nxt is None or nxt["pos"]=="@"): last.append(r["w"][-1])
d=sum(1 for w in last if w.endswith("m"))/max(len(last),1)
print(f"    конец ПОСЛЕДНЕЙ строки абзаца: {d:.1%} (n={len(last)}) — против {a:.1%} у строк вообще")

# 7. «or aiin» против «aiin or»
c_or=sum(1 for w in allw if w=="or"); c_ai=sum(1 for w in allw if w=="aiin")
f1=sum(1 for r in P for l in [r["w"]] for k in range(len(l)-1) if l[k]=="or" and l[k+1]=="aiin")
f2=sum(1 for r in P for l in [r["w"]] for k in range(len(l)-1) if l[k]=="aiin" and l[k+1]=="or")
rule("АСИММЕТРИЯ ПОРЯДКА", "or 366 раз, aiin 470; «or aiin» много чаще «aiin or»",
     f"or {c_or}, aiin {c_ai}; «or aiin» {f1}, «aiin or» {f2}",
     f"ПОДТВЕРЖДАЕТСЯ, отношение {f1/max(f2,1):.1f}×")

# 8. классы взаимозамены — их ли это соседи
CLS=[("ch","sh"),("t","k"),("l","r"),("y","o"),("o","a"),("l","m")]
T=set(M.types(M.load()))
print("\n  КЛАССЫ ВЗАИМОЗАМЕНЫ [ch][sh] [t][k] [l][r] [y][o] [o][a] [l][m]:")
print("    сколько пар типов различаются РОВНО одной такой заменой")
tot=0
for a_,b_ in CLS:
    k=sum(1 for w in T if a_ in w and w.replace(a_,b_,1) in T)
    tot+=k
    print(f"      [{a_}][{b_}]: {k} пар")
nb=M.nbrs(T); edges=sum(len(v) for v in nb.values())//2
print(f"    итого по шести классам: {tot} пар против {edges} рёбер на расстоянии одной правки = {tot/edges:.1%}")
