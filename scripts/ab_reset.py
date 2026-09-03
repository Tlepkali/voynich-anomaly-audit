import json, collections, random, math, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows, pages = D["rows"], D["pages"]
P=[r for r in rows if r["locus"]=="P"]
LINES=[]
for r in P:
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=3:
        LINES.append({"w":ws,"page":r["page"],"L":pages.get(r["page"],{}).get("L","?")})

def lcp(a,b):
    ga,gb=metrics.merge(a),metrics.merge(b); n=0
    for x,y in zip(ga,gb):
        if x!=y: break
        n+=1
    return n
def sim(a,b):
    ga,gb=metrics.merge(a),metrics.merge(b)
    la,lb=len(ga),len(gb)
    prev=list(range(lb+1))
    for i in range(1,la+1):
        cur=[i]+[0]*lb
        for j in range(1,lb+1):
            cur[j]=min(prev[j]+1, cur[j-1]+1, prev[j-1]+(ga[i-1]!=gb[j-1]))
        prev=cur
    return 1-prev[lb]/max(la,lb)

def mean(xs): return sum(xs)/len(xs) if xs else 0.0
def boot(xs, ys, n=400, seed=1):
    """бутстрэп для разности средних: возвращает 95% интервал"""
    rnd=random.Random(seed); ds=[]
    for _ in range(n):
        a=mean([xs[rnd.randrange(len(xs))] for _ in range(len(xs))])
        b=mean([ys[rnd.randrange(len(ys))] for _ in range(len(ys))])
        ds.append(a-b)
    ds.sort(); return ds[int(.025*n)], ds[int(.975*n)]

print("="*78)
print("ПОСТРОЧНЫЙ СБРОС КОПИРОВАНИЯ: A против B")
print("="*78)
print("Мера — похожесть соседних слов (1 − норм. расстояние правки по ЗНАКАМ).")
print("Контроль — те же пары, но партнёр взят из случайного места того же языка.\n")

for lang in ("A","B"):
    ls=[l for l in LINES if l["L"]==lang]
    if len(ls)<300: continue
    rnd=random.Random(42)
    pool=[w for l in ls for w in l["w"]]
    firsts=[l["w"][0] for l in ls]; lasts=[l["w"][-1] for l in ls]

    win_real=[sim(a,b) for l in ls for a,b in zip(l["w"],l["w"][1:])]
    win_ctl =[sim(a, rnd.choice(pool)) for l in ls for a in l["w"][:-1]]

    acr_real=[]; acr_ctl=[]
    for i in range(len(ls)-1):
        if ls[i+1]["page"]!=ls[i]["page"]: continue
        acr_real.append(sim(ls[i]["w"][-1], ls[i+1]["w"][0]))
        acr_ctl .append(sim(ls[i]["w"][-1], rnd.choice(firsts)))

    ew=mean(win_real)-mean(win_ctl); lo_w,hi_w=boot(win_real,win_ctl)
    ea=mean(acr_real)-mean(acr_ctl); lo_a,hi_a=boot(acr_real,acr_ctl)
    print(f"  ЯЗЫК {lang}   строк {len(ls)}, слов {len(pool)}")
    print(f"    внутри строки   пар {len(win_real):5d}   похожесть {mean(win_real):.4f} против контроля {mean(win_ctl):.4f}"
          f"   ИЗБЫТОК {ew:+.4f}  [{lo_w:+.4f}, {hi_w:+.4f}]")
    print(f"    через перенос   пар {len(acr_real):5d}   похожесть {mean(acr_real):.4f} против контроля {mean(acr_ctl):.4f}"
          f"   ИЗБЫТОК {ea:+.4f}  [{lo_a:+.4f}, {hi_a:+.4f}]")
    sig = "ноль внутри интервала — сброс полный" if lo_a<=0<=hi_a else "интервал не накрывает ноль"
    print(f"    → {sig};  отношение избытков внутри/через: {ew/ea:.1f}×" if ea>0 else f"    → {sig}")
    print()

print("="*78)
print("ПОДТВЕРЖДЕНИЕ ДРУГОЙ МЕРОЙ: общий начальный кусок соседних слов (в знаках)")
print("="*78)
for lang in ("A","B"):
    ls=[l for l in LINES if l["L"]==lang]
    if len(ls)<300: continue
    rnd=random.Random(7); pool=[w for l in ls for w in l["w"]]; firsts=[l["w"][0] for l in ls]
    wr=mean([lcp(a,b) for l in ls for a,b in zip(l["w"],l["w"][1:])])
    wc=mean([lcp(a,rnd.choice(pool)) for l in ls for a in l["w"][:-1]])
    ar=[]; ac=[]
    for i in range(len(ls)-1):
        if ls[i+1]["page"]!=ls[i]["page"]: continue
        ar.append(lcp(ls[i]["w"][-1], ls[i+1]["w"][0])); ac.append(lcp(ls[i]["w"][-1], rnd.choice(firsts)))
    print(f"  {lang}: внутри строки {wr:.3f} против {wc:.3f} (избыток {wr-wc:+.3f})   "
          f"через перенос {mean(ar):.3f} против {mean(ac):.3f} (избыток {mean(ar)-mean(ac):+.3f})")

print("\n"+"="*78)
print("ГРУБЫЕ СЧЁТЧИКИ (для полноты; через перенос их мало)")
print("="*78)
for lang in ("A","B"):
    ls=[l for l in LINES if l["L"]==lang]
    if len(ls)<300: continue
    wn=sum(len(l["w"])-1 for l in ls); wrep=sum(1 for l in ls for a,b in zip(l["w"],l["w"][1:]) if a==b)
    an=0; arep=0; prevhit=0
    for i in range(len(ls)-1):
        if ls[i+1]["page"]!=ls[i]["page"]: continue
        an+=1; arep += (ls[i]["w"][-1]==ls[i+1]["w"][0])
        prevhit += (ls[i+1]["w"][0] in set(ls[i]["w"]))
    ctl=sum(1 for i in range(len(ls)-1) if ls[i+1]["page"]==ls[i]["page"]
            and ls[i+1]["w"][len(ls[i+1]["w"])//2] in set(ls[i]["w"]))
    print(f"  {lang}: точный повтор внутри строки {wrep/wn:.2%} ({wrep}/{wn});  через перенос {arep/an:.2%} ({arep}/{an})")
    print(f"     первое слово строки было в предыдущей строке {prevhit/an:.1%};  контроль (слово из середины) {ctl/an:.1%}")
