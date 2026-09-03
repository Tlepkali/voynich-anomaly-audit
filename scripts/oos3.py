# -*- coding: utf-8 -*-
import json, collections, random, sys, math, statistics as st
sys.path.insert(0,"scripts"); sys.path.insert(0,".")
exec(open("scripts/oos.py").read().split("CORP=")[0])
VOY=[w for l in VL for w in l]
CORP={"Войнич (цель)":cutl(VOY), "МОДЕЛЬ":model()}
import os
for nm,fn in [("латынь","latin"),("английский","english"),("немецкий","german"),("итальянский","italian")]:
    p="ref/%s.clean"%fn
    if os.path.exists(p):
        L=cutl(open(p).read().split())
        if L: CORP[nm]=L
def MI(pairs):
    j=collections.Counter(pairs); a=collections.Counter(x for x,_ in pairs); b=collections.Counter(y for _,y in pairs)
    n=len(pairs); return sum(c/n*math.log2((c/n)/((a[x]/n)*(b[y]/n))) for (x,y),c in j.items())
print("="*104); print("3. СТЫК: избыток по 3 знакам против избытка по 1 знаку (равные выборки 12 тыс. слов)"); print("="*104)
print(f"  {'корпус':>16s} {'по 1 знаку':>11s} {'по 3 знакам':>12s} {'отношение':>11s}")
rnd=random.Random(9)
for lab,L in CORP.items():
    def pr(LL,k):
        return [(x[-k:],y[:k]) for l in LL for x,y in zip(l,l[1:])]
    o1,o3=MI(pr(L,1)),MI(pr(L,3)); s1=s3=0.0
    flat=[w for l in L for w in l]
    for _ in range(5):
        sh=flat[:]; rnd.shuffle(sh); i=0; SH=[]
        for l in L: SH.append(sh[i:i+len(l)]); i+=len(l)
        s1+=MI(pr(SH,1))/5; s3+=MI(pr(SH,3))/5
    e1,e3=o1-s1,o3-s3
    print(f"  {lab:>16s} {e1:11.3f} {e3:12.3f} {e3/max(e1,1e-9):10.2f}×")
print("\n"+"="*104); print("4. АВТОКОРРЕЛЯЦИЯ ДЛИНЫ СЛОВА (соседние слова, внутри строки)"); print("="*104)
print(f"  {'корпус':>16s} {'r(d=1)':>8s} {'r(d=2)':>8s} {'r(d=3)':>8s}")
for lab,L in CORP.items():
    row=[]
    for d in (1,2,3):
        xs=[];ys=[]
        for l in L:
            for i in range(len(l)-d): xs.append(len(l[i])); ys.append(len(l[i+d]))
        mx,my=st.mean(xs),st.mean(ys)
        num=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
        den=math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
        row.append(num/den if den else 0)
    print(f"  {lab:>16s} "+" ".join(f"{x:8.3f}" for x in row))
print("\n"+"="*104); print("5. ДРЕЙФ КАК КАРРИЕР: режет ли модель словарь блоками сильнее, чем сама себя"); print("="*104)
def jac(A,B): return len(A&B)/max(len(A|B),1)
def half_vs_cross(L, blocksize):
    flat=[w for l in L for w in l]
    blocks=[flat[i:i+blocksize] for i in range(0,len(flat)-blocksize+1,blocksize)]
    if len(blocks)<4: return None,None
    rnd=random.Random(77); within=[]; cross=[]
    N=blocksize//2
    for b in blocks:
        within.append(jac(set(b[:N]),set(b[N:2*N])))
    for _ in range(200):
        i,j=rnd.randrange(len(blocks)),rnd.randrange(len(blocks))
        if i==j: continue
        cross.append(jac(set(blocks[i][:N]),set(blocks[j][:N])))
    return st.mean(within), st.mean(cross)
print(f"  {'корпус':>16s} {'внутри блока':>13s} {'между блоками':>14s} {'отношение':>11s}   (блок 400 слов ≈ 2 дрейфа модели)")
for lab,L in CORP.items():
    w_,c_=half_vs_cross(L,400)
    if w_: print(f"  {lab:>16s} {w_:13.3f} {c_:14.3f} {c_/max(w_,1e-9):10.2f}×")
print("\n  Для сверки — реальный разрез Карриера на полной рукописи: травник A против травника B даёт 0,116")
print("  при уровне «сам с собой» 0,180–0,206, то есть отношение ≈ 0,60×.")
