# -*- coding: utf-8 -*-
import json, collections, math
D=json.load(open("parsed.json")); P=D["pages"]
LN=[]
for r in D["rows"]:
    if r["locus"]=="P":
        ws=[w for w in r["words"] if '?' not in w]
        if len(ws)>=4: LN.append((r["page"],r["line"],ws))
print("="*104); print("1. КАКИЕ ЗНАКИ ОТКРЫВАЮТ СТРОКУ"); print("="*104)
first=collections.Counter(l[2][0][0] for l in LN)
rest=collections.Counter(w[0] for _,_,ws in LN for w in ws[1:])
tf,tr=sum(first.values()),sum(rest.values())
print(f"  {'знак':>6s} {'в начале строки':>16s} {'в прочих местах':>16s} {'отношение':>11s}")
allk=sorted(set(first)|set(rest), key=lambda k:-(first.get(k,0)/tf))
for k in allk[:11]:
    a,b=first.get(k,0)/tf, rest.get(k,0)/tr
    r=f"{a/b:9.2f}×" if b>0 else "       ∞"
    print(f"  {k:>6s} {a:15.1%} {b:15.1%} {r}")
print("\n"+"="*104); print("2. ДОКУДА ТЯНЕТСЯ: расхождение первых знаков по месту слова в строке"); print("="*104)
def div(c1,c2):
    t1,t2=sum(c1.values()),sum(c2.values())
    ks=set(c1)|set(c2)
    return 0.5*sum(abs(c1.get(k,0)/t1-c2.get(k,0)/t2) for k in ks)
base=collections.Counter(w[0] for _,_,ws in LN for w in ws[3:-1] if len(ws)>5)
print(f"  {'место в строке':>16s} {'расхождение с серединой':>25s}")
for i,lab in ((0,"первое"),(1,"второе"),(2,"третье"),(3,"четвёртое")):
    c=collections.Counter(ws[i][0] for _,_,ws in LN if len(ws)>i)
    print(f"  {lab:>16s} {div(c,base):24.3f}")
last=collections.Counter(ws[-1][0] for _,_,ws in LN)
lastg=collections.Counter(ws[-1][-1] for _,_,ws in LN)
restg=collections.Counter(w[-1] for _,_,ws in LN for w in ws[:-1])
print(f"  {'последнее (первый знак)':>16s} {div(last,base):24.3f}")
print(f"  {'последнее (ПОСЛЕДНИЙ знак)':>16s} {div(lastg,restg):24.3f}")
print("\n"+"="*104); print("3. РЕШАЮЩЕЕ: это другие слова или те же с приставленным знаком?"); print("="*104)
FW=[ws[0] for _,_,ws in LN]
OW=[w for _,_,ws in LN for w in ws[1:]]
ovoc=collections.Counter(OW)
print(f"  слов в начале строки {len(FW)}, из них уже есть в общем словаре: {sum(1 for w in FW if w in ovoc)/len(FW):.1%}")
strip=[w[1:] for w in FW if len(w)>1]
print(f"  если снять первый знак — попадают в общий словарь: {sum(1 for w in strip if w in ovoc)/len(strip):.1%}")
import random
rnd=random.Random(5)
ctrl=[w[1:] for w in rnd.sample(OW,len(strip)) if len(w)>1]
print(f"  контроль (снять первый знак у обычных слов): {sum(1 for w in ctrl if w in ovoc)/len(ctrl):.1%}")
c1=collections.Counter(w[0] for w in strip)
print(f"  расхождение по первому знаку ПОСЛЕ снятия: {div(c1,base):.3f}   (было {div(collections.Counter(w[0] for w in FW),base):.3f})")
ml_f=sum(len(w) for w in FW)/len(FW); ml_o=sum(len(w) for w in OW)/len(OW)
print(f"\n  длина: начало строки {ml_f:.2f}, прочие {ml_o:.2f}, после снятия знака {sum(len(w) for w in strip)/len(strip):.2f}")
print("\n"+"="*104); print("4. ГДЕ ЭФФЕКТ СИЛЬНЕЕ: по контурам, разделам, рукам"); print("="*104)
for key,lab in (("L","язык"),("I","раздел"),("H","рука")):
    g=collections.defaultdict(lambda:[collections.Counter(),collections.Counter()])
    for pg,_,ws in LN:
        v=P.get(pg,{}).get(key,"?")
        g[v][0][ws[0][0]]+=1
        for w in ws[1:]: g[v][1][w[0]]+=1
    rows=[(div(a,b),v,sum(a.values())) for v,(a,b) in g.items() if sum(a.values())>=60]
    rows.sort(reverse=True)
    print(f"  {lab}: " + ", ".join(f"{v}={d:.3f} ({n})" for d,v,n in rows[:6]))
