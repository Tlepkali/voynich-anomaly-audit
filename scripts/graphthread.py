# -*- coding: utf-8 -*-
"""Две находки из курируемой Graph Thread (voynich.ninja/thread-2207):
1. Марко (2018): сравнение ожидаемого и наблюдённого числа случаев, когда
   ПОСЛЕДНЯЯ буква слова совпадает с ПЕРВОЙ буквой следующего. Это мой стык
   в чистейшем частном случае, и найдено до меня.
2. Дэвид Джексон (2018): рукопись подчиняется закону Хипса V = K*N^beta.
   Не мерил вовсе.
"""
import sys, collections, math, random, statistics as st
sys.path.insert(0,"scripts")
import measures as M

VL=M.load(); LENS=[len(l) for l in VL]
def match_rate(L, seed=5, B=20):
    obs=n=0
    for l in L:
        for a,b in zip(l,l[1:]):
            n+=1
            if a[-1]==b[0]: obs+=1
    rnd=random.Random(seed); exp=[]
    for _ in range(B):
        f=[w for x in L for w in x]; rnd.shuffle(f)
        i=0; SH=[]
        for x in L: SH.append(f[i:i+len(x)]); i+=len(x)
        e=sum(1 for x in SH for a,b in zip(x,x[1:]) if a[-1]==b[0])
        exp.append(e)
    return obs/n, st.mean(exp)/n, n
print("="*96); print("1. ПОСЛЕДНЯЯ БУКВА СЛОВА = ПЕРВАЯ БУКВА СЛЕДУЮЩЕГО (Марко, 2018)"); print("="*96)
print(f"  {'корпус':>16s} {'наблюдено':>10s} {'ожидание':>10s} {'отношение':>10s} {'пар':>7s}")
rows=[("ВОЙНИЧ", VL)]
for fn,lab in [("latin.clean","латынь"),("english.clean","английский"),("bk_it.clean","итальянский"),
               ("bk_es.clean","испанский"),("g_herbal.clean","травник"),("scr_vulgata.clean","Вульгата")]:
    rows.append((lab, M.ref_lines(fn,LENS)))
for lab,L in rows:
    o,e,n=match_rate(L)
    print(f"  {lab:>16s} {o:9.2%} {e:9.2%} {o/e:9.2f}× {n:7d}")
print("\n  «ожидание» — перемешивание порядка слов внутри строк, 20 повторов")

print("\n"+"="*96); print("2. ЗАКОН ХИПСА V = K·N^beta (Джексон, 2018)"); print("="*96)
def heaps(tokens):
    seen=set(); pts=[]
    for i,w in enumerate(tokens,1):
        seen.add(w)
        if i in (500,1000,2000,4000,8000,16000,32000) or i==len(tokens): pts.append((i,len(seen)))
    xs=[math.log(a) for a,_ in pts]; ys=[math.log(b) for _,b in pts]
    mx,my=st.mean(xs),st.mean(ys)
    b=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)
    return b, pts
print(f"  {'корпус':>16s} {'beta':>7s}   рост словаря (N→V)")
for lab,L in rows:
    t=M.tokens(L); b,pts=heaps(t)
    tail=", ".join(f"{a//1000}k→{v}" for a,v in pts if a>=4000)
    print(f"  {lab:>16s} {b:7.3f}   {tail}")
print("\n  у естественных языков beta обычно 0,4-0,6")
