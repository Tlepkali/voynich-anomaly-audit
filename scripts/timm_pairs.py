# -*- coding: utf-8 -*-
import json, collections, random, math, os, statistics as st
def lev1(a,b):
    """расстояние правки ≤1 (быстрая проверка)"""
    if a==b: return 0
    la,lb=len(a),len(b)
    if abs(la-lb)>1: return 2
    if la==lb:
        d=0
        for x,y in zip(a,b):
            if x!=y:
                d+=1
                if d>1: return 2
        return d
    s,l=(a,b) if la<lb else (b,a)
    for i in range(len(l)):
        if l[:i]+l[i+1:]==s: return 1
    return 2
def count_pairs(seq, n, sample=3500, maxd=1, seed=1):
    """доля пар n-грамм, отличающихся не более чем на maxd правок суммарно"""
    rnd=random.Random(seed)
    pos=[i for i in range(len(seq)-n+1)]
    if len(pos)>sample: pos=rnd.sample(pos,sample)
    grams=[tuple(seq[i:i+n]) for i in pos]
    hit=0; tot=0
    for i in range(len(grams)):
        gi=grams[i]
        for j in range(i+1,len(grams)):
            gj=grams[j]; tot+=1
            d=0
            for a,b in zip(gi,gj):
                d+=lev1(a,b)
                if d>maxd: break
            if d<=maxd: hit+=1
    return hit, tot, hit/tot
D=json.load(open("parsed.json"))
pg=collections.defaultdict(list)
for r in D["rows"]:
    if r["locus"]=="P":
        ws=[w for w in r["words"] if '?' not in w]
        if ws: pg[r["page"]].extend(ws)
VOY=[w for v in pg.values() for w in v]
print("="*100)
print("ПАРЫ ТИММА: почти одинаковые отрезки. Больше ли их, чем даёт плотность словаря?")
print("="*100)
rnd=random.Random(5)
def shuffled_pages():
    out=[]
    for v in pg.values():
        c=v[:]; rnd.shuffle(c); out.extend(c)
    return out
SH=shuffled_pages()
print(f"  {'длина отрезка':>14s} {'наблюдается':>13s} {'при перемешивании':>19s} {'превышение':>12s}")
for n in (2,3,4):
    h1,t1,p1=count_pairs(VOY,n)
    h2,t2,p2=count_pairs(SH,n,seed=2)
    print(f"  {n:>14d} {p1:12.5%} {p2:18.5%} {p1/max(p2,1e-12):11.2f}×")
print("\n  перемешивание внутри страницы сохраняет словарь и его плотность,")
print("  разрушая только порядок слов — то есть ровно то, что и есть «пара»")
print("\n" + "="*100)
print("ТО ЖЕ НА ЯЗЫКАХ")
print("="*100)
print(f"  {'корпус':>14s} {'n=2 набл.':>11s} {'n=2 перемеш.':>14s} {'превышение':>12s}")
for tag,lab in (("latin","латынь"),("english","английский"),("wiki_de","немецкий")):
    p=f"ref/{tag}.clean"
    if not os.path.exists(p): continue
    ws=open(p).read().split()[:len(VOY)]
    sh=ws[:]; rnd.shuffle(sh)
    h1,t1,a=count_pairs(ws,2,seed=3)
    h2,t2,b=count_pairs(sh,2,seed=4)
    print(f"  {lab:>14s} {a:10.5%} {b:13.5%} {a/max(b,1e-12):11.2f}×")
h1,t1,a=count_pairs(VOY,2)
h2,t2,b=count_pairs(SH,2,seed=2)
print(f"  {'Войнич':>14s} {a:10.5%} {b:13.5%} {a/max(b,1e-12):11.2f}×")
