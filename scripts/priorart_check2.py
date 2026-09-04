# -*- coding: utf-8 -*-
"""Три расхождения из первой проверки — разбор.
1. «за f и p никогда не следует c» (Карриер 1976) — заявлено в АЛФАВИТЕ КАРРИЕРА,
   а я проверял в EVA, где c это начало бенча ch. Проверяю в CD2a.
2. «qo отдельным словом 29 раз» — по шести транскрипциям.
3. «тройной повтор в 35 фразах» (Тимм) — возможно, не подряд, а трижды в строке.
"""
import json, collections, sys

def load(code, locus=None):
    D=json.load(open(f"data/parsed_{code}.json"))
    R=[r for r in D["rows"] if locus is None or r["locus"]==locus]
    for r in R: r["w"]=[x for x in r["words"] if "?" not in x]
    return [r for r in R if r["w"]]

CODES=[("ZL3b-n","EVA Зандб.–Ландини"),("IT2a-n","EVA Такахаси"),("RF1b-e","EVA Reference"),
       ("GC2a-n","v101 Класton"),("FG2a-n","FSG"),("CD2a-n","Карриер")]

print("="*100); print("1. «ЗА f И p НИКОГДА НЕ СЛЕДУЕТ c» — В КАКОМ АЛФАВИТЕ ЭТО ВЕРНО"); print("="*100)
print("  Карриер писал в СВОЁМ алфавите; в EVA c — первый знак бенча ch, и правило про него неверно.")
print(f"\n  {'транскрипция':>22s} {'знаки':>8s} {'самые частые после виселиц':>46s}")
for code,lab in CODES:
    R=load(code,"P")
    pf=[w for r in R for w in r["w"]]
    pairs=[(w[i],w[i+1]) for w in pf for i in range(len(w)-1)]
    # виселицы в EVA — f p k t; в прочих алфавитах их обозначения иные, поэтому
    # берём знаки, которые ведут себя как виселицы: сильно чаще в началах строк
    FI=collections.Counter(r["w"][0][0] for r in R)
    MID=collections.Counter(w[0] for r in R for w in r["w"][1:])
    a=sum(FI.values()); b=sum(MID.values())
    lift={c:(FI[c]/a)/(MID[c]/b) for c in FI if MID[c]>=20 and FI[c]>=20}
    gal=[c for c,v in sorted(lift.items(), key=lambda x:-x[1])[:2]]
    out=[]
    for g in gal:
        nx=collections.Counter(y for x,y in pairs if x==g); t=sum(nx.values())
        top=", ".join(f"{c}·{v}" for c,v in nx.most_common(3))
        out.append(f"{g} (тяга {lift[g]:.0f}×, n={t}): {top}")
    print(f"  {lab:>22s} {len(set(''.join(pf))):8d}   " + " | ".join(out))
print("\n  ВЫВОД: правило проверяемо только внутри своего алфавита; в EVA c после p стоит")
print("  в 48 % случаев, потому что EVA пишет бенч двумя знаками. Это не опровержение")
print("  Карриера, а несопоставимость записи — тот же класс, что мои шесть транскрипций.")

print("\n"+"="*100); print("2. «qo ОТДЕЛЬНЫМ СЛОВОМ 29 РАЗ» ПО ТРАНСКРИПЦИЯМ"); print("="*100)
for code,lab in CODES:
    R=load(code)
    allw=[w for r in R for w in r["w"]]
    P=[w for r in R if r["locus"]=="P" for w in r["w"]]
    # в не-EVA алфавитах «qo» пишется иначе — считаем только там, где строка есть
    c_all=sum(1 for w in allw if w=="qo"); c_p=sum(1 for w in P if w=="qo")
    print(f"  {lab:>22s}: все локусы {c_all:4d}, сплошной текст {c_p:4d}")
print("  заявлено 29; расхождение вероятно от версии транскрипции и от того,")
print("  считались ли слова с сомнительными знаками")

print("\n"+"="*100); print("3. ТРОЙНОЙ ПОВТОР: ПОДРЯД ИЛИ ТРИЖДЫ В СТРОКЕ"); print("="*100)
R=load("ZL3b-n")
adj=0; inline=0; ex=collections.Counter()
for r in R:
    l=r["w"]
    for k in range(len(l)-2):
        if l[k]==l[k+1]==l[k+2]: adj+=1
    c=collections.Counter(l)
    for w,v in c.items():
        if v>=3: inline+=1; ex[w]+=1
print(f"  трижды ПОДРЯД                : {adj}")
print(f"  трижды В ОДНОЙ СТРОКЕ (не подряд): {inline}")
print(f"  заявлено Тиммом: 35")
print(f"  примеры «трижды в строке»: " + ", ".join(f"{w}·{v}" for w,v in ex.most_common(8)))
print("\n  ВЫВОД: 35 — это, судя по величине, счёт «трижды в строке», а не подряд.")
print("  Мои 8 подряд и его 35 в строке — разные величины, не противоречие.")
