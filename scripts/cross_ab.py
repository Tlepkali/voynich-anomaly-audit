import json, collections, math, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
TOK={"A":[], "B":[]}
for r in [r for r in rows if r["locus"]=="P"]:
    L=pages.get(r["page"],{}).get("L","?")
    if L in TOK: TOK[L]+= [w for w in r["words"] if '?' not in w]
N=min(len(TOK["A"]), len(TOK["B"]))
def gl(w): return ["^"]+metrics.merge(w)+["$"]
def mean(x): return sum(x)/len(x) if x else 0.0

def train(types, V):
    c=collections.Counter(); ctx=collections.Counter()
    for w in types:
        g=gl(w)
        for a,b in zip(g,g[1:]): c[(a,b)]+=1; ctx[a]+=1
    return c, ctx
def xent(model, types, V, k=0.5):
    c,ctx=model; tot=0.0; n=0
    for w in types:
        g=gl(w)
        for a,b in zip(g,g[1:]):
            p=(c[(a,b)]+k)/(ctx[a]+k*V); tot-=math.log2(p); n+=1
    return tot/n
def coverage(model, types):
    """доля слов, у которых ВСЕ переходы встречались в обучающем языке"""
    c,_=model; ok=0
    for w in types:
        g=gl(w)
        if all(c[(a,b)]>0 for a,b in zip(g,g[1:])): ok+=1
    return ok/len(types)

print("="*88)
print("ПЕРЕКРЁСТНАЯ ПРОВЕРКА: модель формы слова, обученная на одном языке, на другом")
print("обучение и проверка на ТИПАХ при равном объёме просмотренных токенов; 10 повторов")
print("="*88)
res=collections.defaultdict(list)
for k in range(10):
    r=random.Random(400+k)
    ty={L: list(collections.Counter(r.sample(TOK[L],N))) for L in ("A","B")}
    V=len({g for L in ty for w in ty[L] for g in gl(w)})
    # половина типов на обучение, половина на проверку — чтобы «свой на своём» не был завышен
    for L in ("A","B"):
        r.shuffle(ty[L])
    half={L: (ty[L][:len(ty[L])//2], ty[L][len(ty[L])//2:]) for L in ("A","B")}
    mA=train(half["A"][0], V); mB=train(half["B"][0], V)
    res["A→A"].append(xent(mA, half["A"][1], V)); res["A→B"].append(xent(mA, half["B"][1], V))
    res["B→B"].append(xent(mB, half["B"][1], V)); res["B→A"].append(xent(mB, half["A"][1], V))
    res["покрытие A→B"].append(coverage(mA, half["B"][1]))
    res["покрытие B→A"].append(coverage(mB, half["A"][1]))
    res["покрытие A→A"].append(coverage(mA, half["A"][1]))
    res["покрытие B→B"].append(coverage(mB, half["B"][1]))
print("  Стоимость описания слова, бит на знак (меньше — модель лучше подходит):")
print(f"     A на своих  {mean(res['A→A']):.3f}      A на словах B  {mean(res['A→B']):.3f}   "
      f"штраф +{mean(res['A→B'])-mean(res['A→A']):.3f}")
print(f"     B на своих  {mean(res['B→B']):.3f}      B на словах A  {mean(res['B→A']):.3f}   "
      f"штраф +{mean(res['B→A'])-mean(res['B→B']):.3f}")
print("\n  Покрытие: доля слов, все переходы которых встречались в обучающем языке:")
print(f"     A→A {mean(res['покрытие A→A']):.1%}    A→B {mean(res['покрытие A→B']):.1%}")
print(f"     B→B {mean(res['покрытие B→B']):.1%}    B→A {mean(res['покрытие B→A']):.1%}")

print("\n"+"="*88)
print("ЧТО ЗА СЛОВА В ОБЩЕЙ ЧАСТИ СЛОВАРЯ, А ЧТО В СОБСТВЕННЫХ")
print("="*88)
sa=set(TOK["A"]); sb=set(TOK["B"]); inter=sa&sb
def prof(ws, name):
    ln=[len(metrics.merge(w)) for w in ws]; mu=mean(ln)
    ca=collections.Counter(TOK["A"]); cb=collections.Counter(TOK["B"])
    print(f"  {name:26s} слов {len(ws):5d}   ср.длина {mu:4.2f}   "
          f"пример: {', '.join(sorted(ws, key=lambda w:-(ca[w]+cb[w]))[:6])}")
prof(inter, "общие для A и B")
prof(sa-sb, "только A")
prof(sb-sa, "только B")
ca=collections.Counter(TOK["A"]); cb=collections.Counter(TOK["B"])
sh_a=sum(ca[w] for w in inter)/sum(ca.values()); sh_b=sum(cb[w] for w in inter)/sum(cb.values())
print(f"\n  доля ТЕКСТА, покрытая общими словами: в A {sh_a:.1%}, в B {sh_b:.1%}")
