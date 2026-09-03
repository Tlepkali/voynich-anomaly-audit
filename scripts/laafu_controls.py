# -*- coding: utf-8 -*-
import json, collections, math, statistics as st, random
D=json.load(open("parsed.json"))
LN=[[w for w in r["words"] if '?' not in w] for r in D["rows"] if r["locus"]=="P"]
LN=[l for l in LN if len(l)>=5]
voc=collections.Counter(w for l in LN for w in l[1:])
first=[l[0] for l in LN]
second=[l[1] for l in LN]
last=[l[-1] for l in LN]
mid=[w for l in LN for w in l[1:-1]]
def div(c1,c2):
    t1,t2=sum(c1.values()),sum(c2.values())
    return 0.5*sum(abs(c1.get(k,0)/t1-c2.get(k,0)/t2) for k in set(c1)|set(c2))
print("="*98)
print("КОНТРОЛИ ПОД LAAFU")
print("="*98)
base=collections.Counter(w[0] for w in mid)
print("\n  1. РАСХОЖДЕНИЕ ПЕРВЫХ БУКВ — остаётся ли оно после снятия приписанного знака")
d_raw=div(collections.Counter(w[0] for w in first), base)
# снимаем первый знак там, где остаток есть в словаре (т.е. приписывание правдоподобно)
strip=[w[1:] if (len(w)>1 and w[1:] in voc) else w for w in first]
d_str=div(collections.Counter(w[0] for w in strip), base)
n_str=sum(1 for w in first if len(w)>1 and w[1:] in voc)
print(f"     как есть:                    {d_raw:.3f}")
print(f"     после снятия (снято {n_str} из {len(first)}): {d_str:.3f}")
print(f"     остаётся: {d_str/d_raw:.0%} исходного расхождения")
print("\n  2. ДЛИНА ПЕРВОГО СЛОВА — объясняется ли приписанным знаком")
print(f"     первое слово:      {st.mean([len(w) for w in first]):.3f}")
print(f"     после снятия:      {st.mean([len(w) for w in strip]):.3f}")
print(f"     середина строки:   {st.mean([len(w) for w in mid]):.3f}")
print("\n  3. ВТОРОЕ СЛОВО КОРОЧЕ — правда ли, и с каким контролем")
print(f"     второе слово:      {st.mean([len(w) for w in second]):.3f}")
print(f"     середина строки:   {st.mean([len(w) for w in mid]):.3f}")
# контроль: длина как функция места вообще
byp=collections.defaultdict(list)
for l in LN:
    n=len(l)-1
    for i,w in enumerate(l): byp[i].append(len(w))
print("     длина по номеру слова: " + " ".join(f"{i+1}:{st.mean(byp[i]):.2f}" for i in range(6)))
print("\n  4. КОНЕЦ СТРОКИ НА m — величина и есть ли у m позиционный запрет")
em_last=sum(1 for w in last if w.endswith("m"))/len(last)
em_mid=sum(1 for w in mid if w.endswith("m"))/len(mid)
print(f"     последнее слово кончается на m: {em_last:.1%}")
print(f"     слово в середине:               {em_mid:.1%}")
print(f"     превышение: {em_last/max(em_mid,1e-9):.1f}×")
allm=[(i/(len(l)-1) if len(l)>1 else 0) for l in LN for i,w in enumerate(l) if w.endswith("m")]
print(f"     всего слов на m: {len(allm)}, среднее место {st.mean(allm):.3f}, в последней пятой {sum(1 for p in allm if p>0.8)/len(allm):.0%}")
# а есть ли у m пара без m
pairs=[(w,w[:-1]) for w in set(x for l in LN for x in l) if w.endswith("m") and len(w)>1]
inv=sum(1 for a,b in pairs if voc.get(b,0)>=5)
print(f"     форм на m: {len(pairs)}, из них основа без m есть в словаре: {inv} ({inv/len(pairs):.0%})")
