# -*- coding: utf-8 -*-
"""Дэвис 2020 различила ПЯТЬ писцов по НАЧЕРТАНИЮ (DigiPal, цифровая
палеография). Боуэрн и Линдеманн отмечают изоморфизм: писец 1 пишет на языке A,
писцы 2-5 на языке B.

ВОПРОС, КОТОРОГО НЕ ЗАДАВАЛИ: различается ли ТЕКСТ разных рук СВЕРХ различия
языков Карриера? Если да — «пять языков» Заттеры получают опору. Если нет —
различие рук чисто палеографическое.

Сравниваю ВНУТРИ языка B (руки 2, 3, 4, 5), база — рука против самой себя.
"""
import re, json, collections, random, statistics as st, sys
sys.path.insert(0,"scripts")
raw=open("data/ZL3b-n.txt",encoding="utf-8",errors="ignore").read()
PAGE={}
for m in re.finditer(r"^<(f[^>]*?)>\s+<!([^>]*)>", raw, re.M):
    PAGE[m.group(1)]=dict(re.findall(r"\$([A-Z])=(\S+)", m.group(2)))
D=json.load(open("data/parsed.json"))
rows=[]
for r in D["rows"]:
    if r["locus"]!="P": continue
    w=[x for x in r["words"] if "?" not in x]
    if len(w)<3: continue
    v=PAGE.get(r["page"],{})
    rows.append(dict(page=r["page"], w=w, L=v.get("L"), H=v.get("H")))
print("="*96); print("РУКИ И ЯЗЫКИ: сколько токенов в каждой паре"); print("="*96)
c=collections.Counter((r["H"],r["L"]) for r in rows)
t=collections.Counter()
for r in rows: t[(r["H"],r["L"])]+=len(r["w"])
for k in sorted(t, key=lambda x:-t[x]):
    if t[k]<300: continue
    print(f"  рука {str(k[0]):>4s}, язык {str(k[1]):>4s}: строк {c[k]:4d}, токенов {t[k]:6d}")
def bag(rs): return collections.Counter(w for r in rs for w in r["w"])
def cos(a,b):
    ks=set(a)|set(b); na=sum(v*v for v in a.values())**.5; nb=sum(v*v for v in b.values())**.5
    return sum(a[k]*b[k] for k in ks)/(na*nb) if na and nb else float("nan")
def cut(rs,n):
    out=[];k=0
    for r in rs:
        out.append(r); k+=len(r["w"])
        if k>=n: break
    return out
def halves(rs,seed):
    pg=sorted({r["page"] for r in rs}); rnd=random.Random(seed); rnd.shuffle(pg)
    h=set(pg[:len(pg)//2])
    return [r for r in rs if r["page"] in h], [r for r in rs if r["page"] not in h]

for LANG in ("B","A"):
    H=[h for h in ("1","2","3","4","5") if t.get((h,LANG),0)>=2000]
    if len(H)<2: 
        print(f"\n  язык {LANG}: рук с достаточным объёмом меньше двух ({H})"); continue
    print("\n"+"="*96); print(f"ВНУТРИ ЯЗЫКА {LANG}: РУКИ ДРУГ ПРОТИВ ДРУГА, база — рука против самой себя"); print("="*96)
    n=min(t[(h,LANG)] for h in H)
    print(f"  руки {H}, выравнено по {n} токенов")
    grp={h: cut([r for r in rows if r["H"]==h and r["L"]==LANG], n) for h in H}
    print(f"\n  {'пара':>12s} {'косинус':>9s}")
    between=[]
    for i in range(len(H)):
        for j in range(i+1,len(H)):
            v=cos(bag(grp[H[i]]), bag(grp[H[j]])); between.append(v)
            print(f"  {H[i]+' против '+H[j]:>12s} {v:9.3f}")
    within=[]
    for h in H:
        vs=[]
        for s in range(8):
            a,b=halves(grp[h],s)
            if a and b: vs.append(cos(bag(a),bag(b)))
        if vs: within.append(st.mean(vs)); print(f"  {'рука '+h+' сама':>12s} {st.mean(vs):9.3f}")
    print(f"\n  между руками {st.mean(between):.3f} [{min(between):.3f}; {max(between):.3f}]")
    print(f"  внутри руки  {st.mean(within):.3f} [{min(within):.3f}; {max(within):.3f}]")
    print(f"  → {'РУКИ РАЗЛИЧАЮТСЯ ТЕКСТОМ' if max(between)<min(within) else 'различие рук НЕ превышает внутреннего'}")

# ── КОНТРОЛЬ: не раздел ли это ─────────────────────────────────────────────
print("\n"+"="*96); print("КОНТРОЛЬ: руки 2 и 3 ВНУТРИ ОДНОГО ТИПА ИЛЛЮСТРАЦИИ ($I)"); print("="*96)
for r in rows: r["I"]=PAGE.get(r["page"],{}).get("I")
combo=collections.Counter()
for r in rows:
    if r["L"]=="B" and r["H"] in ("2","3"): combo[(r["H"],r["I"])]+=len(r["w"])
print("  токенов по (рука, тип иллюстрации):")
for k in sorted(combo, key=lambda x:-combo[x]):
    if combo[k]>=200: print(f"    рука {k[0]}, {str(k[1]):>5s}: {combo[k]:6d}")
shared=[i for i in {k[1] for k in combo} if combo.get(("2",i),0)>=1500 and combo.get(("3",i),0)>=1500]
print(f"\n  типы, где ОБЕ руки пишут достаточно: {shared}")
for I in shared:
    g2=[r for r in rows if r["L"]=="B" and r["H"]=="2" and r["I"]==I]
    g3=[r for r in rows if r["L"]=="B" and r["H"]=="3" and r["I"]==I]
    n=min(sum(len(r["w"]) for r in g2), sum(len(r["w"]) for r in g3))
    g2,g3=cut(g2,n),cut(g3,n)
    b=cos(bag(g2),bag(g3))
    w=[]
    for g in (g2,g3):
        vs=[]
        for s in range(8):
            a,bb=halves(g,s)
            if a and bb: vs.append(cos(bag(a),bag(bb)))
        if vs: w.append(st.mean(vs))
    print(f"\n  тип {I}, выравнено по {n} токенов:")
    print(f"    между руками {b:.3f}, внутри руки {st.mean(w):.3f} [{min(w):.3f}; {max(w):.3f}]")
    print(f"    → {'различие рук ДЕРЖИТСЯ внутри одного раздела' if b<min(w) else 'различие СНИМАЕТСЯ разделом'}")
