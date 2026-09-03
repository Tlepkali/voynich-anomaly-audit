import json, collections, math
D=json.load(open("parsed.json")); rows, pages = D["rows"], D["pages"]
P=[r for r in rows if r["locus"]=="P"]
LINES=[]
for r in P:
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=3: LINES.append({"w":ws,"pos":r["pos"],"page":r["page"]})
ALL=[w for l in LINES for w in l["w"]]
VOC=collections.Counter(ALL)
FIRST=[l["w"][0] for l in LINES]; LAST=[l["w"][-1] for l in LINES]
MID=[w for l in LINES for w in l["w"][1:-1]]

def wilson(k,n):
    if n==0: return (0,0)
    p=k/n; z=1.96; d=1+z*z/n
    c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (c-h, c+h)

print("="*72)
print("ТЕСТ 1. Начальное слово строки = обычное слово с приписанной буквой?")
print("="*72)
print("  снимаем первую букву и смотрим, есть ли остаток в словаре рукописи\n")
print(f"  {'буква':6s} {'позиция':12s} {'n':>6s} {'остаток — слово':>17s} {'95% интервал':>18s}")
for g in "pftkyds":
    for name, ws in (("начало строки",FIRST),("середина",MID)):
        sel=[w for w in ws if w and w[0]==g and len(w)>2]
        if len(sel)<25: continue
        k=sum(1 for w in sel if w[1:] in VOC)
        lo,hi=wilson(k,len(sel))
        print(f"  {g:6s} {name:12s} {len(sel):6d} {k/len(sel):16.1%}  [{lo:5.1%}, {hi:5.1%}]")
    print()

print("="*72)
print("ТЕСТ 2. Знак m: буква или пометка конца строки?")
print("="*72)
m_words=[w for w in ALL if 'm' in w]
m_final_pos=sum(1 for w in m_words if w.endswith('m'))
print(f"  слов со знаком m: {len(m_words)}, из них m стоит в конце слова: {m_final_pos} ({m_final_pos/len(m_words):.0%})")
last_m=sum(1 for w in LAST if w.endswith('m'))
mid_m =sum(1 for w in MID if w.endswith('m'))
first_m=sum(1 for w in FIRST if w.endswith('m'))
tot_m=last_m+mid_m+first_m
print(f"  все слова, кончающиеся на m: {tot_m}")
print(f"     в конце строки  {last_m:5d}  ({last_m/tot_m:.0%} от всех)   — доля таких слов среди концов строк: {last_m/len(LAST):.1%}")
print(f"     в середине      {mid_m:5d}  ({mid_m/tot_m:.0%})              среди середины: {mid_m/len(MID):.1%}")
print(f"     в начале строки {first_m:5d}  ({first_m/tot_m:.0%})")
print(f"  → перевес в {(last_m/len(LAST))/(mid_m/len(MID)):.0f} раз")

print("\n"+"="*72)
print("ТЕСТ 3. Словарь краёв строки: свой или общий?")
print("="*72)
sf=set(FIRST); sl=set(LAST); sm=set(MID)
print(f"  типов в начале строки {len(sf):5d}, из них не встречаются в середине: {len(sf-sm):4d} ({len(sf-sm)/len(sf):.0%})")
print(f"  типов в конце строки  {len(sl):5d}, из них не встречаются в середине: {len(sl-sm):4d} ({len(sl-sm)/len(sl):.0%})")
import random
rnd=random.Random(3)
ctrl=[rnd.choice(MID) for _ in range(len(FIRST))]
sc=set(ctrl)
print(f"  контроль: та же выборка из середины — {len(sc):5d} типов, уникальных: {len(sc-set(MID))} (0% по построению)")
print(f"  средняя частота слова: начало {sum(VOC[w] for w in FIRST)/len(FIRST):6.1f}   "
      f"середина {sum(VOC[w] for w in MID)/len(MID):6.1f}   конец {sum(VOC[w] for w in LAST)/len(LAST):6.1f}")

print("\n"+"="*72)
print("ТЕСТ 4. Копирование слов уважает границу строки?")
print("="*72)
within=0; wn=0; across=0; an=0
for i,l in enumerate(LINES):
    ws=l["w"]
    for a,b in zip(ws,ws[1:]):
        wn+=1; within += (a==b)
    if i+1<len(LINES) and LINES[i+1]["page"]==l["page"]:
        an+=1; across += (ws[-1]==LINES[i+1]["w"][0])
print(f"  повтор внутри строки:       {within:4d} / {wn:5d} = {within/wn:.2%}")
print(f"  повтор через перенос строки:{across:4d} / {an:5d} = {across/an:.2%}")
print(f"  → внутри строки повторы {(within/wn)/max(across/an,1e-9):.1f}× чаще")

print("\n"+"="*72)
print("ТЕСТ 5. Одинаков ли эффект в языках A и B?")
print("="*72)
for lang in ("A","B"):
    ls=[l for l in LINES if pages.get(l["page"],{}).get("L")==lang]
    if len(ls)<200: continue
    f=[l["w"][0] for l in ls]; m=[w for l in ls for w in l["w"][1:-1]]; la=[l["w"][-1] for l in ls]
    cf=collections.Counter(w[0] for w in f); cm=collections.Counter(w[0] for w in m)
    Tf=len(f); Tm=len(m)
    div=0.5*sum(abs(cf.get(k,0)/Tf-cm.get(k,0)/Tm) for k in set(cf)|set(cm))
    mm=sum(1 for w in la if w.endswith('m'))/len(la)
    fl=sum(len(w) for w in f)/len(f); ml=sum(len(w) for w in m)/len(m)
    print(f"  {lang}: строк {len(ls):5d}  расхождение первых букв {div:.3f}   "
          f"m в конце строки {mm:5.1%}   длина 1-го слова {fl:.2f} против {ml:.2f} в середине")
