# -*- coding: utf-8 -*-
import json, collections, random, statistics as st, math
D=json.load(open("parsed.json"))
def rows(loc): return [(r["page"],[w for w in r["words"] if '?' not in w]) for r in D["rows"] if r["locus"]==loc]
P=[w for _,ws in rows("P") for w in ws]
Craw=rows("C"); Rraw=rows("R"); Lraw=rows("L")
# отсеиваем «алфавитные» строки: где больше половины слов односимвольные
C=[(pg,ws) for pg,ws in Craw if ws and sum(1 for w in ws if len(w)==1)/len(ws)<0.5]
drop=[(pg,ws) for pg,ws in Craw if ws and sum(1 for w in ws if len(w)==1)/len(ws)>=0.5]
print("="*96); print("ОТСЕВ АЛФАВИТНЫХ СТРОК"); print("="*96)
print(f"  колец всего {len(Craw)}, отсеяно {len(drop)}: " + ", ".join(f"{pg} ({len(ws)} слов)" for pg,ws in drop[:5]))
Cw=[w for _,ws in C for w in ws]; Rw=[w for _,ws in Rraw for w in ws]; Lw=[w for _,ws in Lraw for w in ws]
print(f"  осталось: круговой {len(Cw)} слов, радиальный {len(Rw)}, подписи {len(Lw)}")
vp=collections.Counter(P)
def prof(ws, lab):
    c=collections.Counter(ws)
    return (lab, len(ws), len(c)/len(ws), sum(1 for v in c.values() if v==1)/len(c),
            sum(1 for w in ws if w in vp)/len(ws), sum(1 for w in ws if w[0]=='o')/len(ws),
            st.mean(len(w) for w in ws))
print("\n" + "="*96); print("ЧЕТЫРЕ ВИДА ПИСЬМА В ОДНОЙ РУКОПИСИ"); print("="*96)
print(f"  {'вид':>14s} {'слов':>6s} {'TTR':>6s} {'хапакс':>7s} {'есть в тексте':>14s} {'на o':>7s} {'длина':>6s}")
for ws,lab in ((P,"сплошной"),(Cw,"круговой"),(Rw,"радиальный"),(Lw,"подписи")):
    _,n,t,h,i,o,l=prof(ws,lab)
    print(f"  {lab:>14s} {n:6d} {t:6.3f} {h:7.3f} {i:13.0%} {o:6.0%} {l:6.2f}")
print("\n  «есть в тексте» и «на o» у сплошного текста — сам с собой, для шкалы")
print("\n" + "="*96)
print("ГЛАВНОЕ: есть ли приписывание в начале КОЛЬЦА (строк там нет)")
print("="*96)
firstC=[ws[0] for _,ws in C if ws]
restC=[w for _,ws in C for w in ws[1:]]
firstP=[ws[0] for _,ws in rows("P") if ws]
restP=[w for _,ws in rows("P") for w in ws[1:]]
def strip_rate(ws, against):
    a=[w for w in ws if len(w)>1]
    return sum(1 for w in a if w[1:] in against)/len(a), len(a)
vocC=collections.Counter(restC); vocP=collections.Counter(restP)
a,na=strip_rate(firstC, vocP); b,nb=strip_rate(restC, vocP)
print(f"  КРУГОВОЙ: первое слово кольца разбирается в {a:.0%} ({na} слов), прочие слова кольца — {b:.0%} ({nb})")
c,nc=strip_rate(firstP, vocP); d,nd=strip_rate(restP, vocP)
print(f"  СПЛОШНОЙ: первое слово строки {c:.0%} ({nc}), прочие {d:.0%} ({nd})")
fc=collections.Counter(w[0] for w in firstC); tc=sum(fc.values())
rc=collections.Counter(w[0] for w in restC); tr=sum(rc.values())
print(f"\n  первый знак первого слова кольца против прочих слов кольца:")
for k,_ in fc.most_common(5):
    print(f"    {k}: {fc[k]/tc:5.1%} против {rc.get(k,0)/tr:5.1%}")
