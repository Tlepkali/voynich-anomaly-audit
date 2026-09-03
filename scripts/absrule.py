import json, collections, math, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
SEC={"H":"травник","P":"аптечный","B":"«банный»","T":"текст","C":"космол.","S":"рецепты"}
LINES=[]
for r in [r for r in rows if r["locus"]=="P"]:
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=3:
        m=pages.get(r["page"],{})
        LINES.append({"w":ws,"page":r["page"],"L":m.get("L","?"),"I":m.get("I","?"),"H":m.get("H","?")})
def gl(w): return metrics.merge(w)

def pois_tail(obs, exp):
    """вероятность увидеть obs или меньше при ожидании exp"""
    if exp>500: 
        z=(obs-exp)/math.sqrt(exp); return 0.5*math.erfc(-z/math.sqrt(2))
    s=0.0
    for k in range(obs+1): s += math.exp(-exp + k*math.log(exp) - math.lgamma(k+1))
    return min(1.0, s)

CELLS=[("1","H"),("1","P"),("2","B"),("2","H"),("2","T"),("3","S"),("3","H"),("5","H")]
print("="*100)
print("ПОИСК КАТЕГОРИЧЕСКИХ ЗАПРЕТОВ: знак в конце слова, который почти не встречается ВНЕ конца строки")
print("порог: ожидание вне конца строки ≥ 15 наблюдений (иначе нет силы теста)")
print("="*100)
for h,s in CELLS:
    ls=[l for l in LINES if l["H"]==h and l["I"]==s]
    if len(ls)<55: continue
    lastw=[l["w"][-1] for l in ls]; midw=[w for l in ls for w in l["w"][:-1]]
    p_mid=len(midw)/(len(midw)+len(lastw))
    cnt_end=collections.Counter(gl(w)[-1] for w in lastw)
    cnt_mid=collections.Counter(gl(w)[-1] for w in midw)
    lang="".join(sorted({l["L"] for l in ls}))
    hits=[]
    for g in set(cnt_end)|set(cnt_mid):
        n=cnt_end[g]+cnt_mid[g]; exp=n*p_mid
        if exp<15: continue
        obs=cnt_mid[g]
        if obs < 0.35*exp:
            hits.append((pois_tail(obs,exp), g, obs, exp, n))
    hits.sort()
    tag=f"рука {h} · {SEC.get(s,s)} [{lang}]"
    if hits:
        print(f"\n  {tag:26s} строк {len(ls):5d}")
        for pv,g,obs,exp,n in hits[:4]:
            print(f"     знак «{g}»: всего {n:5d}   вне конца строки {obs:4d} при ожидании {exp:7.1f}"
                  f"   утечка {obs/exp:5.1%}   p={pv:.1e}")
    else:
        print(f"\n  {tag:26s} строк {len(ls):5d}   — категорических запретов не найдено")

print("\n"+"="*100)
print("ТО ЖЕ ДЛЯ НАЧАЛА СТРОКИ: знак в начале слова, редкий вне начала строки")
print("="*100)
for h,s in CELLS:
    ls=[l for l in LINES if l["H"]==h and l["I"]==s]
    if len(ls)<55: continue
    firstw=[l["w"][0] for l in ls]; restw=[w for l in ls for w in l["w"][1:]]
    p_rest=len(restw)/(len(restw)+len(firstw))
    ce=collections.Counter(gl(w)[0] for w in firstw)
    cm=collections.Counter(gl(w)[0] for w in restw)
    hits=[]
    for g in set(ce)|set(cm):
        n=ce[g]+cm[g]; exp=n*p_rest
        if exp<15: continue
        obs=cm[g]
        if obs < 0.35*exp: hits.append((pois_tail(obs,exp), g, obs, exp, n))
    hits.sort()
    tag=f"рука {h} · {SEC.get(s,s)}"
    if hits:
        print(f"  {tag:26s}  " + ";  ".join(
            f"«{g}» {obs}/{exp:.0f} (утечка {obs/exp:.0%}, p={pv:.0e})" for pv,g,obs,exp,n in hits[:3]))
    else:
        print(f"  {tag:26s}  — нет")
