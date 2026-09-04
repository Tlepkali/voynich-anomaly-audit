# -*- coding: utf-8 -*-
"""«Рукопись заметно лишена повторяющихся многословных фраз, в отличие от
средневековых травников» — Зандберген, voynich.nu/a5_synt, как одна из главных
аномалий. Травник у меня в наборе есть, проверяю прямо и с выравниванием."""
import sys, collections, random, statistics as st
sys.path.insert(0,"scripts")
import measures as M
VL=M.load(); LENS=[len(l) for l in VL]; N=sum(LENS)
def rep(L, n):
    """доля n-грамм слов, встречающихся более одного раза"""
    g=collections.Counter()
    for l in L:
        for i in range(len(l)-n+1): g[tuple(l[i:i+n])]+=1
    tot=sum(g.values())
    return sum(v for v in g.values() if v>1)/max(tot,1), tot
CORP=[("ВОЙНИЧ", VL)]
for fn,lab in [("g_herbal.clean","травник (жанр!)"),("g_apicius.clean","Апиций"),
               ("latin.clean","латынь"),("scr_vulgata.clean","Вульгата"),
               ("english.clean","английский"),("bk_it.clean","итальянский"),
               ("bk_es.clean","испанский"),("bk_fr1.clean","французский")]:
    L=M.ref_lines(fn,LENS)
    if sum(len(l) for l in L)>N*0.9: CORP.append((lab,L))
print("="*96); print("ПОВТОРЯЮЩИЕСЯ n-ГРАММЫ СЛОВ (доля вхождений, встречающихся больше раза)"); print("="*96)
print(f"  {'корпус':>18s} {'биграммы':>10s} {'триграммы':>11s} {'4-граммы':>10s}")
for lab,L in CORP:
    r2,_=rep(L,2); r3,_=rep(L,3); r4,_=rep(L,4)
    print(f"  {lab:>18s} {r2:9.2%} {r3:10.2%} {r4:9.2%}")
print("\n  нуль для рукописи — перемешивание слов ВНУТРИ СТРОКИ (тема цела, порядок разрушен):")
rnd=random.Random(3)
for n in (2,3):
    obs,_=rep(VL,n)
    nl=[]
    for s in range(20):
        r=random.Random(100+s); SH=[]
        for l in VL:
            c=l[:]; r.shuffle(c); SH.append(c)
        nl.append(rep(SH,n)[0])
    print(f"    {n}-граммы: наблюдено {obs:.2%}, нуль {st.mean(nl):.2%} [{min(nl):.2%}; {max(nl):.2%}]")
