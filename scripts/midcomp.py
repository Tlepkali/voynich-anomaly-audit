import re, collections, sys
sys.path.insert(0,"."); import metrics
alt=re.compile(r'\[([^\]]*)\]')
def clean(t):
    t=re.sub(r'<[^>]*>','',t); t=re.sub(r'\{[^}]*\}','',t)
    t=alt.sub(lambda m:m.group(1).split(':')[0],t)
    t=re.sub(r'@\d+;','',t).replace("'","").replace('!','').replace('%','')
    return re.sub(r'[-=~/]','',t.replace(',','.'))
LINES=[]
for line in open("ZL3b-n.txt", encoding="utf-8", errors="replace"):
    m=re.match(r'^<(f[0-9]+[rv][0-9]*)\.([0-9]+),([@+=*&])(P)([A-Za-z0-9]?)>\s*(.*)$', line)
    if not m: continue
    ws=[w for w in clean(m.group(6)).split('.') if w and '?' not in w]
    if len(ws)>=3: LINES.append({"w":ws,"pf":'<$>' in m.group(6)})
MID=[w for l in LINES for w in l["w"][1:-1]]
FIN=[l["w"][-1] for l in LINES if not l["pf"]]
BEG=[l["w"][0] for l in LINES]
def gl(w): return metrics.merge(w)
print(f"слов: середина {len(MID)}, конец строки {len(FIN)}, начало {len(BEG)}\n")

print("="*86)
print("ИЗ ЧЕГО СОСТОЯТ СЛОВА: доля СЛОВ, содержащих знак")
print("="*86)
def share(ws):
    c=collections.Counter()
    for w in ws:
        for g in set(gl(w)): c[g]+=1
    return {g:v/len(ws) for g,v in c.items()}
sm, sf, sb = share(MID), share(FIN), share(BEG)
keys=sorted(set(sm)|set(sf), key=lambda g:-sm.get(g,0))
print(f"  {'знак':8s} {'состав':9s} {'середина':>9s} {'конец стр':>10s} {'начало':>8s} {'конец/середина':>16s}")
for g in keys:
    if max(sm.get(g,0), sf.get(g,0))<0.02: continue
    kind="составной" if len(g)>1 else "простой"
    r=(sf.get(g,0)+1e-9)/(sm.get(g,0)+1e-9)
    mark=" ←" if (r>1.5 or r<0.55) else ""
    print(f"  {g:8s} {kind:9s} {sm.get(g,0):9.1%} {sf.get(g,0):10.1%} {sb.get(g,0):8.1%} {r:15.2f}{mark}")

print("\n"+"="*86)
print("ГДЕ ЖИВУТ СОСТАВНЫЕ ЗНАКИ")
print("="*86)
for name, ws in (("середина строки",MID),("конец строки",FIN),("начало строки",BEG)):
    tot=sum(len(gl(w)) for w in ws)
    comp=collections.Counter(g for w in ws for g in gl(w) if len(g)>1)
    n=sum(comp.values())
    top=", ".join(f"{g} {v/tot:.1%}" for g,v in comp.most_common(6))
    print(f"  {name:16s} составных знаков {n/tot:5.1%} от всех   из них: {top}")

print("\n"+"="*86)
print("СТРОЕНИЕ СЛОВА В СЕРЕДИНЕ СТРОКИ: что стоит в начале, внутри, в конце")
print("="*86)
pos=collections.defaultdict(collections.Counter)
for w in MID:
    g=gl(w)
    if len(g)==1: pos["одиночное"][g[0]]+=1; continue
    pos["начало"][g[0]]+=1; pos["конец"][g[-1]]+=1
    for x in g[1:-1]: pos["внутри"][x]+=1
for k in ("начало","внутри","конец"):
    T=sum(pos[k].values())
    print(f"  {k:8s} " + "  ".join(f"{g} {v/T:.0%}" for g,v in pos[k].most_common(7)))

print("\n"+"="*86)
print("САМЫЕ ЧАСТЫЕ СХЕМЫ СЛОВ В СЕРЕДИНЕ СТРОКИ")
print("="*86)
tpl=collections.Counter(" ".join(gl(w)) for w in MID)
for t,n in tpl.most_common(12):
    print(f"  {t:34s} {n:5d}  {n/len(MID):5.2%}   ({t.replace(' ','')})")
print(f"\n  разных схем: {len(tpl)}; десять самых частых покрывают "
      f"{sum(n for _,n in tpl.most_common(10))/len(MID):.1%} слов середины строки")
