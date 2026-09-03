# -*- coding: utf-8 -*-
"""Остаток строки: сидит ли он в ПЕРВОЙ строке абзаца.

ПРЕДСКАЗАНИЕ, ОБЪЯВЛЕНО ДО ЗАПУСКА. Если остаток после приписывания есть
явление верхней строки абзаца (слова Гроува, строки Тилтмана, ключи Нила),
то на строках-ПРОДОЛЖЕНИЯХ (pos '+') приписывание при p, оценённом по длине,
должно объяснять расхождение почти целиком, а избыток p/t/f — сидеть в
строках с pos '@'. Если остаток одинаков в обеих группах, дело не в абзаце.
"""
import json, collections, statistics as st
D=json.load(open("data/parsed.json"))
ROWS=[r for r in D["rows"] if r["locus"]=="P" and len([w for w in r["words"] if "?" not in w])>=3]
for r in ROWS: r["w"]=[w for w in r["words"] if "?" not in w]
VT={w for r in ROWS for w in r["w"]}
MID=[w for r in ROWS for w in r["w"][1:]]
mid=collections.Counter(w[0] for w in MID); b=sum(mid.values())
midlen=st.mean(len(w) for w in MID)

def analyse(rows, lab):
    FI=[r["w"][0] for r in rows]
    if len(FI)<50: return None
    fi=collections.Counter(w[0] for w in FI); a=sum(fi.values())
    PRE=collections.Counter(w[0] for w in FI if len(w)>2 and w[1:] in VT); pt=sum(PRE.values())
    p=st.mean(len(w) for w in FI)-midlen                      # доля приписывания по длине
    raw=sum(abs(fi[c]/a-mid[c]/b) for c in set(fi)|set(mid))/2
    res=0.0; per={}
    for c in set(fi)|set(mid):
        pred=p*(PRE[c]/pt if pt else 0)+(1-p)*mid[c]/b
        per[c]=fi[c]/a-pred; res+=abs(per[c])
    res/=2
    G={g: (sum(1 for w in FI if w.startswith(g))/len(FI))/(sum(1 for w in MID if w.startswith(g))/len(MID))
       for g in "pftk"}
    grove=sum(1 for w in FI if len(w)>2 and w[1:] in VT)/len(FI)
    return dict(lab=lab, n=len(FI), p=p, raw=raw, res=res, per=per, G=G, grove=grove)

print("="*104); print("РАСХОЖДЕНИЕ ПО ТИПУ СТРОКИ"); print("="*104)
GRP=[("ВСЕ строки", ROWS),
     ("@ первая строка абзаца", [r for r in ROWS if r["pos"]=="@"]),
     ("+ продолжение абзаца",   [r for r in ROWS if r["pos"]=="+"]),
     ("прочие (&, =, *)",       [r for r in ROWS if r["pos"] not in ("@","+")])]
R=[]
print(f"  {'группа':>24s} {'строк':>6s} {'p по длине':>11s} {'сырое':>8s} {'остаток':>8s} {'доля ост.':>10s} {'Гроув':>7s}")
for lab,rows in GRP:
    r=analyse(rows,lab)
    if not r: continue
    R.append(r)
    print(f"  {lab:>24s} {r['n']:6d} {r['p']:11.2f} {r['raw']:8.3f} {r['res']:8.3f} {r['res']/r['raw']:9.0%} {r['grove']:7.1%}")
print("\n"+"="*104); print("ВИСЕЛИЦЫ: во сколько раз чаще в начале строки, чем в середине"); print("="*104)
print(f"  {'группа':>24s} " + " ".join(f"{g:>8s}" for g in "pftk"))
for r in R:
    print(f"  {r['lab']:>24s} " + " ".join(f"{r['G'][g]:7.1f}×" for g in "pftk"))
print("\n"+"="*104); print("ОСТАТОК ПО ЗНАКАМ (наблюдённое минус предсказанное приписыванием)"); print("="*104)
keys=[c for c,_ in sorted(mid.items(), key=lambda x:-x[1])][:10]
print(f"  {'группа':>24s} " + " ".join(f"{c:>7s}" for c in keys))
for r in R:
    print(f"  {r['lab']:>24s} " + " ".join(f"{r['per'].get(c,0):+6.1%}" for c in keys))
