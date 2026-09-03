# -*- coding: utf-8 -*-
import json, collections, math, random, statistics as st
D=json.load(open("parsed.json")); PG=D["pages"]
NAME={"H":"травник","B":"«банный»","S":"звёзды","T":"текст","C":"космология","P":"аптечный","A":"астрономия","Z":"зодиак"}
sec=collections.defaultdict(list); seclang=collections.defaultdict(collections.Counter)
for r in D["rows"]:
    if r["locus"]!="P": continue
    m=PG.get(r["page"],{}); s=m.get("I","?")
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=2:
        sec[s].append((m.get("L","?"),ws))
        seclang[s][m.get("L","?")]+=len(ws)
print("="*104); print("РАЗДЕЛЫ И ЯЗЫКИ КАРРИЕРА: сцеплены ли"); print("="*104)
print(f"  {'раздел':>13s} {'слов':>7s} {'строк':>6s} {'A':>6s} {'B':>6s}")
for s in sorted(sec, key=lambda k:-sum(len(w) for _,w in sec[k])):
    n=sum(len(w) for _,w in sec[s]); c=seclang[s]; t=sum(c.values())
    if n<400: continue
    print(f"  {NAME.get(s,s):>13s} {n:7,d} {len(sec[s]):6d} {c.get('A',0)/t:5.0%} {c.get('B',0)/t:5.0%}")
def adj(lines):
    obs=sum(1 for l in lines for i in range(len(l)-1) if l[i]==l[i+1])
    rnd=random.Random(2); acc=0.0
    for _ in range(10):
        for l in lines:
            p=rnd.sample(l,len(l)); acc+=sum(1 for a,b in zip(p,p[1:]) if a==b)/10
    return obs, acc, obs/max(acc,.01)
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
def chains(lines):
    o=0
    for l in lines:
        for i in range(len(l)-1):
            if near(l[i],l[i+1]): o+=1
    rnd=random.Random(3); acc=0.0
    for _ in range(6):
        for l in lines:
            p=rnd.sample(l,len(l))
            acc+=sum(1 for a,b in zip(p,p[1:]) if near(a,b))/6
    return o/max(acc,.01)
def batt(lines, lab):
    flat=[w for l in lines for w in l]
    c=collections.Counter(flat)
    o,e,r=adj(lines)
    return (lab, len(flat), r, chains(lines), len(c)/len(flat),
            sum(1 for w in flat if w[0]=='o')/len(flat), st.mean(len(w) for w in flat))
print("\n" + "="*104); print("БАТАРЕЯ ПО РАЗДЕЛАМ"); print("="*104)
print(f"  {'раздел':>13s} {'слов':>7s} {'соседство':>10s} {'цепочки':>9s} {'TTR':>7s} {'на o':>7s} {'длина':>7s}")
big=[s for s in sec if sum(len(w) for _,w in sec[s])>=1500]
res=[]
for s in sorted(big, key=lambda k:-sum(len(w) for _,w in sec[k])):
    b=batt([w for _,w in sec[s]], NAME.get(s,s)); res.append((s,b))
    print(f"  {b[0]:>13s} {b[1]:7,d} {b[2]:9.2f}× {b[3]:8.2f}× {b[4]:7.3f} {b[5]:6.0%} {b[6]:7.2f}")
print("\n" + "="*104); print("ТО ЖЕ ВНУТРИ ЯЗЫКА B (снимаем сцепленность с контуром)"); print("="*104)
print(f"  {'раздел':>13s} {'слов':>7s} {'соседство':>10s} {'цепочки':>9s} {'TTR':>7s} {'на o':>7s} {'длина':>7s}")
for s in sorted(big, key=lambda k:-sum(len(w) for _,w in sec[k])):
    ls=[w for L,w in sec[s] if L=="B"]
    n=sum(len(w) for w in ls)
    if n<1200: continue
    b=batt(ls, NAME.get(s,s))
    print(f"  {b[0]:>13s} {b[1]:7,d} {b[2]:9.2f}× {b[3]:8.2f}× {b[4]:7.3f} {b[5]:6.0%} {b[6]:7.2f}")
