# -*- coding: utf-8 -*-
"""Два утверждения со страниц Зандбергена (a4_word), которых у меня нет.
1. «Примерно половина типов встречается один раз» — у меня E3 даёт 69,7 %.
2. Стольфи: распределение длин ТИПОВ «почти идеально биномиально», что
   «необычно для естественного языка». Не мерил вовсе.
"""
import sys, json, collections, math, statistics as st
sys.path.insert(0,"scripts")
import measures as M

print("="*96); print("1. ДОЛЯ ГАПАКСОВ: от охвата"); print("="*96)
D=json.load(open("data/parsed.json"))
def hap(rows, locus=None):
    ws=[w for r in rows if (locus is None or r["locus"]==locus) for w in r["words"] if "?" not in w]
    c=collections.Counter(ws)
    return sum(1 for v in c.values() if v==1)/len(c), len(ws), len(c)
for lab,loc in [("сплошной текст (мой охват)","P"),("ВСЕ локусы (охват Зандбергена)",None)]:
    h,nt,ty=hap(D["rows"],loc)
    print(f"  {lab:>32s}: токенов {nt:6d}, типов {ty:5d}, гапаксов {h:.1%}")
print("\n  у Зандбергена «примерно половина», у Редди-Найта 8114 типов на 37 919 токенов")
print("  РАЗНИЦА НЕ В ОХВАТЕ: даже на всех локусах доля далеко от половины.")
print("  Вероятно, «половина» — округление вниз или иная транскрипция; проверяю по шести:")
for code,lab in [("ZL3b-n","EVA Зандб.–Ландини"),("IT2a-n","EVA Такахаси"),("RF1b-e","EVA Reference"),
                 ("GC2a-n","v101 Класton"),("FG2a-n","FSG"),("CD2a-n","Карриер")]:
    d=json.load(open(f"data/parsed_{code}.json"))
    ws=[w for r in d["rows"] for w in r["words"] if "?" not in w]
    c=collections.Counter(ws)
    print(f"    {lab:>22s}: токенов {len(ws):6d}, типов {len(c):5d}, гапаксов {sum(1 for v in c.values() if v==1)/len(c):.1%}")

print("\n"+"="*96); print("2. БИНОМИАЛЬНОСТЬ ДЛИН ТИПОВ (Стольфи)"); print("="*96)
def fit(T, lab):
    L=[len(w) for w in T]; n=max(L); m=st.mean(L)
    p=m/n
    obs=collections.Counter(L); N=len(L)
    # хи-квадрат к биномиальному B(n,p) и к геометрическому для сравнения
    def binom(k): return math.comb(n,k)*p**k*(1-p)**(n-k)
    chi=0; used=0
    for k in range(1,n+1):
        e=N*binom(k)
        if e>=5: chi+=(obs[k]-e)**2/e; used+=1
    return m, st.pstdev(L), chi/max(used,1), used
print(f"  {'корпус':>16s} {'ср.длина':>9s} {'sd':>6s} {'хи2/степень':>12s}")
TV=M.types(M.load())
m_,sd_,c_,u_=fit(TV,"Войнич"); print(f"  {'ВОЙНИЧ':>16s} {m_:9.2f} {sd_:6.2f} {c_:12.1f}")
for fn,lab in [("latin.clean","латынь"),("english.clean","английский"),("bk_it.clean","итальянский"),
               ("bk_es.clean","испанский"),("g_herbal.clean","травник"),("scr_vulgata.clean","Вульгата")]:
    T=sorted(set(M.ref(fn,34024)))
    m_,sd_,c_,u_=fit(T,lab); print(f"  {lab:>16s} {m_:9.2f} {sd_:6.2f} {c_:12.1f}")
print("\n  чем МЕНЬШЕ хи2 на степень свободы, тем ближе к биномиальному")
print("  (мера грубая: сравниваем не подгонку, а во сколько раз рукопись ближе прочих)")
