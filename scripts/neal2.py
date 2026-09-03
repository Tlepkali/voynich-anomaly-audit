# -*- coding: utf-8 -*-
import json, collections, math
D=json.load(open("parsed.json")); PG=D["pages"]
rows=[r for r in D["rows"] if r["locus"]=="P"]
def clean(r): return [w for w in r["words"] if '?' not in w]
TOP={"@","="}
def has(w,gl): return any(g in w for g in gl)
SL="pf"; DL="tk"
print("="*98); print("ОСНОВА: доля слов с одноногой виселицей (p/f) по типу строки"); print("="*98)
print(f"  {'тип строки':>28s} {'строк':>6s} {'слов':>7s} {'p/f':>7s} {'t/k':>7s}")
for lab,sel in [("верхняя строка абзаца", lambda r: r["pos"] in TOP), ("продолжение абзаца", lambda r: r["pos"]=="+")]:
    ls=[clean(r) for r in rows if sel(r)]; f=[w for l in ls for w in l]
    print(f"  {lab:>28s} {len(ls):6d} {len(f):7,d} {sum(1 for w in f if has(w,SL))/len(f):6.1%} {sum(1 for w in f if has(w,DL))/len(f):6.1%}")
for lab,sel in [("  из них 1-е слово строки", 0), ("  из них не 1-е слово", 1)]:
    ls=[clean(r) for r in rows if r["pos"] in TOP]
    f=[l[0] for l in ls if l] if sel==0 else [w for l in ls for w in l[1:]]
    print(f"  {lab:>28s} {'':6s} {len(f):7,d} {sum(1 for w in f if has(w,SL))/len(f):6.1%} {sum(1 for w in f if has(w,DL))/len(f):6.1%}")
print("\n"+"="*98); print("КЛЮЧ НИЛА: смежные пары p/f-слов на верхней строке, кроме первого слова"); print("="*98)
def neal(lines, gl=SL):
    obs=0; exp=0.0; pairs=0; klines=0
    for l in lines:
        t=l[1:]                      # исключаем слово, начинающее абзац (слова Гроува)
        n=len(t)
        if n<2: continue
        k=sum(1 for w in t if has(w,gl))
        obs+=sum(1 for i in range(n-1) if has(t[i],gl) and has(t[i+1],gl))
        exp+=k*(k-1)/(n-1)           # точное ожидание при перестановке ВНУТРИ строки
        pairs+=n-1
        if k>=2: klines+=1
    return obs, exp, pairs, klines
ls=[clean(r) for r in rows if r["pos"] in TOP]
o,e,pr,kl=neal(ls)
print(f"  верхних строк: {len(ls)}, из них с ≥2 одноногими (кроме 1-го слова): {kl}")
print(f"  смежных пар всего: {pr:,d}")
print(f"  наблюдено ключей Нила: {o}  ({o/pr:.2%} пар)")
print(f"  ожидание при перестановке внутри строки: {e:.1f}  ({e/pr:.2%} пар)")
print(f"  ОТНОШЕНИЕ: {o/max(e,.01):.2f}×")
var=e  # приближение Пуассона для p-значения
z=(o-e)/math.sqrt(max(e,1e-9))
print(f"  z ≈ {z:+.2f}")
print("\n  Для сравнения — то же на строках-продолжениях:")
ls2=[clean(r) for r in rows if r["pos"]=="+"]
o2,e2,pr2,kl2=neal(ls2)
print(f"  наблюдено {o2} ({o2/pr2:.2%}), ожидание {e2:.1f} ({e2/pr2:.2%}), отношение {o2/max(e2,.01):.2f}×, z ≈ {(o2-e2)/math.sqrt(max(e2,1e-9)):+.2f}")
print("\n  Контроль двуногими виселицами (t/k) на тех же верхних строках:")
o3,e3,pr3,kl3=neal(ls,DL)
print(f"  наблюдено {o3} ({o3/pr3:.2%}), ожидание {e3:.1f} ({e3/pr3:.2%}), отношение {o3/max(e3,.01):.2f}×, z ≈ {(o3-e3)/math.sqrt(max(e3,1e-9)):+.2f}")
