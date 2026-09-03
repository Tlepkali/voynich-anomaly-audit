# -*- coding: utf-8 -*-
import json, collections, math, random
D=json.load(open("parsed.json")); P=D["pages"]
LN=[]
for r in D["rows"]:
    if r["locus"]=="P":
        ws=[w for w in r["words"] if '?' not in w]
        if len(ws)>=4: LN.append((P.get(r["page"],{}),ws))
voc=collections.Counter(w for _,ws in LN for w in ws[1:])   # словарь БЕЗ первых слов
print("="*100)
print("КОНТРОЛИ ПОД СЛОВА ГРОУВА")
print("утверждение: редкие слова в началах строк = обычное слово с приписанным галлоусом")
print("="*100)
def strip_test(sel_first, sel_other, lab):
    a=[w for w in sel_first if len(w)>1]
    b=[w for w in sel_other if len(w)>1]
    if len(a)<25 or len(b)<25: return None
    pa=sum(1 for w in a if w[1:] in voc)/len(a)
    pb=sum(1 for w in b if w[1:] in voc)/len(b)
    p=(sum(1 for w in a if w[1:] in voc)+sum(1 for w in b if w[1:] in voc))/(len(a)+len(b))
    se=math.sqrt(max(1e-12,p*(1-p)*(1/len(a)+1/len(b))))
    return pa,pb,(pa-pb)/se,len(a),len(b)
print(f"\n  1. СНЯТИЕ ГАЛЛОУСА: попадает ли остаток в словарь")
print(f"     {'знак':>5s} {'строк':>6s} {'в начале строки':>16s} {'те же знаки не в начале':>24s} {'z':>7s}")
for g in ("p","f","t","k","d","s","y","o","q","c"):
    first=[ws[0] for _,ws in LN if ws[0].startswith(g)]
    other=[w for _,ws in LN for w in ws[1:] if w.startswith(g)]
    r=strip_test(first,other,g)
    if r is None:
        print(f"     {g:>5s} {len(first):6d}   данных мало"); continue
    pa,pb,z,na,nb=r
    mark="  ←" if z>4 else ""
    print(f"     {g:>5s} {na:6d} {pa:15.1%} {pb:23.1%} {z:7.1f}{mark}")
print(f"\n  2. РЕДКИ ЛИ ОНИ: доля слов, встречающихся в рукописи один раз")
allc=collections.Counter(w for _,ws in LN for w in ws)
print(f"     {'группа':>28s} {'слов':>6s} {'хапаксов':>10s}")
grp=[("первое слово строки, галлоус p/f", lambda i,w: i==0 and (w[0] in "pf")),
     ("первое слово строки, прочее",      lambda i,w: i==0 and (w[0] not in "pf")),
     ("не первое слово, галлоус p/f",     lambda i,w: i>0 and (w[0] in "pf")),
     ("не первое слово, прочее",          lambda i,w: i>0 and (w[0] not in "pf"))]
for lab,f in grp:
    sel=[w for _,ws in LN for i,w in enumerate(ws) if f(i,w)]
    if not sel: continue
    hap=sum(1 for w in sel if allc[w]==1)/len(sel)
    print(f"     {lab:>28s} {len(sel):6d} {hap:9.1%}")
print(f"\n  3. ДЛИНА: длиннее ли слова Гроува обычных")
import statistics as st
for lab,f in grp:
    sel=[w for _,ws in LN for i,w in enumerate(ws) if f(i,w)]
    if len(sel)<30: continue
    st2=[len(w)-1 for w in sel if len(w)>1]
    print(f"     {lab:>28s}: длина {st.mean([len(w) for w in sel]):.2f}, после снятия знака {st.mean(st2):.2f}")
