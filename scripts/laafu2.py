# -*- coding: utf-8 -*-
import json, collections, random
D=json.load(open("parsed.json")); P=D["pages"]
LN=[]
for r in D["rows"]:
    if r["locus"]=="P":
        ws=[w for w in r["words"] if '?' not in w]
        if len(ws)>=4: LN.append((r["page"],ws))
FW=[ws[0] for _,ws in LN]
OW=[w for _,ws in LN for w in ws[1:]]
ovoc=collections.Counter(OW)
print("="*100); print("КАКОЙ ЗНАК ПРИСТАВЛЕН: разбор по снятому знаку"); print("="*100)
rnd=random.Random(5); SAMP=rnd.sample(OW, 3000)
def rate(words):
    g=collections.defaultdict(lambda:[0,0])
    for w in words:
        if len(w)<2: continue
        g[w[0]][0]+=1
        if w[1:] in ovoc: g[w[0]][1]+=1
    return g
gf=rate(FW); go=rate(SAMP)
print(f"  {'знак':>6s} {'в начале строк':>15s} {'из них после снятия':>21s} {'у обычных слов':>16s} {'разница':>9s}")
rows=[]
for k,(n,h) in gf.items():
    if n<40: continue
    n2,h2=go.get(k,[0,0])
    if n2<20: continue
    rows.append((h/n-h2/n2, k, n, h/n, n2, h2/n2))
rows.sort(reverse=True)
for d,k,n,a,n2,b in rows:
    print(f"  {k:>6s} {n:15d} {a:20.1%} {b:15.1%} {d:+8.1%}")
print("\n" + "="*100); print("ГАЛЛОУСЫ p f t k В НАЧАЛЕ СТРОКИ: доля строк, где первое слово с ними"); print("="*100)
gal=set("pftk")
n_g=sum(1 for w in FW if w[0] in gal); n_o=sum(1 for w in OW if w[0] in gal)
print(f"  первое слово строки: {n_g/len(FW):.1%};  прочие слова: {n_o/len(OW):.1%};  превышение {(n_g/len(FW))/(n_o/len(OW)):.2f}×")
# только p и f — «настоящие» декоративные
pf=set("pf")
a=sum(1 for w in FW if w[0] in pf)/len(FW); b=sum(1 for w in OW if w[0] in pf)/len(OW)
print(f"  только p и f:        {a:.1%};  прочие: {b:.1%};  превышение {a/b:.2f}×")
print("\n" + "="*100); print("ГДЕ ИМЕННО В СТРОКЕ СТОЯТ p и f"); print("="*100)
pos=collections.Counter(); tot=collections.Counter()
for _,ws in LN:
    n=len(ws)
    for i,w in enumerate(ws):
        b_=min(int(i/n*5),4); tot[b_]+=1
        if w[0] in pf: pos[b_]+=1
print("  " + " ".join(f"{'пятая '+str(i+1)}: {pos[i]/tot[i]:.2%}" for i in range(5)))
print("\n" + "="*100); print("ТА ЖЕ ПРОВЕРКА ПО РУКАМ: у кого приставка чаще"); print("="*100)
g=collections.defaultdict(lambda:[0,0,0,0])
for pg,ws in LN:
    hnd=P.get(pg,{}).get("H","?")
    g[hnd][0]+=1
    if ws[0][0] in pf: g[hnd][1]+=1
    if len(ws[0])>1 and ws[0][1:] in ovoc: g[hnd][2]+=1
    g[hnd][3]+=len(ws[0])
for hnd,(n,p_,s,ln) in sorted(g.items(), key=lambda x:-x[1][0]):
    if n<80: continue
    print(f"  рука {hnd}: строк {n:5d}, первое слово с p/f {p_/n:5.1%}, после снятия знака в словаре {s/n:5.1%}, длина {ln/n:.2f}")
