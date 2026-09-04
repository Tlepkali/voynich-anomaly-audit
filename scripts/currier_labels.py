# -*- coding: utf-8 -*-
"""Метки $L (язык Карриера) и $H (рука) лежат в самом файле IVTFF, а мой парсер
их выбрасывал. Запись D1 «языки A и B статистически различны» проверялась без
них. Плюс с апреля 2024 у Зандбергена ТРИ RZ-языка (A, B, C), где C —
промежуточный и покрывает астрономические страницы, которые Карриер не
классифицировал вовсе. Смотрю, сколько рукописи вне классификации."""
import re, collections, json, sys, statistics as st, random
sys.path.insert(0,"scripts")
import measures as M

raw=open("data/ZL3b-n.txt",encoding="utf-8",errors="ignore").read()
PAGE={}
for m in re.finditer(r"^<(f[^>]*?)>\s+<!([^>]*)>", raw, re.M):
    pg=m.group(1); v=dict(re.findall(r"\$([A-Z])=(\S+)", m.group(2)))
    PAGE[pg]=v
D=json.load(open("data/parsed.json"))
rows=[r for r in D["rows"] if r["locus"]=="P"]
for r in rows: r["w"]=[w for w in r["words"] if "?" not in w]
rows=[r for r in rows if len(r["w"])>=3]
lab=collections.Counter(PAGE.get(r["page"],{}).get("L","(нет метки)") for r in rows)
tok=collections.Counter()
for r in rows: tok[PAGE.get(r["page"],{}).get("L","(нет метки)")]+=len(r["w"])
print("="*90); print("ОХВАТ КЛАССИФИКАЦИИ КАРРИЕРА В СПЛОШНОМ ТЕКСТЕ"); print("="*90)
for k in sorted(lab, key=lambda x:-tok[x]):
    print(f"  язык {k:>12s}: строк {lab[k]:5d}, токенов {tok[k]:6d} ({tok[k]/sum(tok.values()):.1%})")
print(f"\n  ВНЕ КЛАССИФИКАЦИИ {tok.get('(нет метки)',0)/sum(tok.values()):.1%} сплошного текста —")
print("  это территория RZ-языка C (Зандберген, апрель 2024), которую я проверить не могу")
h=collections.Counter(PAGE.get(r["page"],{}).get("H","(нет)") for r in rows)
print(f"\n  руки ($H): " + ", ".join(f"{k}·{v}" for k,v in sorted(h.items())))

print("\n"+"="*90); print("A ПРОТИВ B ПО ОФИЦИАЛЬНЫМ МЕТКАМ, БАЗА — ЯЗЫК ПРОТИВ САМОГО СЕБЯ"); print("="*90)
def bag(rs): return collections.Counter(w for r in rs for w in r["w"])
def jac(a,b):
    A,B=set(a),set(b); return len(A&B)/len(A|B)
def cosine(a,b):
    ks=set(a)|set(b); na=sum(v*v for v in a.values())**.5; nb=sum(v*v for v in b.values())**.5
    return sum(a[k]*b[k] for k in ks)/(na*nb)
A=[r for r in rows if PAGE.get(r["page"],{}).get("L")=="A"]
B=[r for r in rows if PAGE.get(r["page"],{}).get("L")=="B"]
print(f"  A: строк {len(A)}, токенов {sum(len(r['w']) for r in A)}")
print(f"  B: строк {len(B)}, токенов {sum(len(r['w']) for r in B)}")
def halves(rs, seed):
    pgs=sorted({r["page"] for r in rs}); rnd=random.Random(seed); rnd.shuffle(pgs)
    h=set(pgs[:len(pgs)//2])
    return [r for r in rs if r["page"] in h], [r for r in rs if r["page"] not in h]
n=min(sum(len(r['w']) for r in A), sum(len(r['w']) for r in B))
def cut(rs, n):
    out=[]; t=0
    for r in rs:
        out.append(r); t+=len(r["w"])
        if t>=n: break
    return out
Ac, Bc = cut(A,n), cut(B,n)
print(f"\n  выравнено по {n} токенов")
print(f"  {'сравнение':>28s} {'Жаккар':>8s} {'косинус':>9s}")
print(f"  {'A против B':>28s} {jac(bag(Ac),bag(Bc)):8.3f} {cosine(bag(Ac),bag(Bc)):9.3f}")
ja=[];jb=[];ca=[];cb=[]
for s in range(10):
    a1,a2=halves(Ac,s); b1,b2=halves(Bc,s)
    ja.append(jac(bag(a1),bag(a2))); ca.append(cosine(bag(a1),bag(a2)))
    jb.append(jac(bag(b1),bag(b2))); cb.append(cosine(bag(b1),bag(b2)))
print(f"  {'A против самого себя':>28s} {st.mean(ja):8.3f} {st.mean(ca):9.3f}")
print(f"  {'B против самого себя':>28s} {st.mean(jb):8.3f} {st.mean(cb):9.3f}")
print(f"\n  различие A/B {'ПРЕВЫШАЕТ' if jac(bag(Ac),bag(Bc))<min(st.mean(ja),st.mean(jb)) else 'НЕ превышает'} внутриязыковое")
