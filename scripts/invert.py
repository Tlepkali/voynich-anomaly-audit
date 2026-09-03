import json, collections, random, sys, itertools
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
TOK={"A":[],"B":[]}
for r in [r for r in rows if r["locus"]=="P"]:
    L=pages.get(r["page"],{}).get("L","?")
    if L in TOK: TOK[L]+=[w for w in r["words"] if '?' not in w]
cA=collections.Counter(TOK["A"]); cB=collections.Counter(TOK["B"])
SA=set(cA); SB=set(cB)
def gl(w): return metrics.merge(w)
GA={w:gl(w) for w in SA}

# три найденных правила, как условные переписывания
def apply_rules(g, rules):
    """возвращает множество вариантов: каждое правило применимо или нет в каждой точке"""
    out={tuple(g)}
    for (src, dsts, cond) in rules:
        new=set()
        for v in out:
            new.add(v)
            for i,x in enumerate(v):
                if x!=src: continue
                if not cond(v,i): continue
                for d in dsts:
                    new.add(v[:i]+(d,)+v[i+1:])
        out=new
    return out
R_before_d = lambda v,i: i+1<len(v) and v[i+1] in ("d","dy")
R_not_final= lambda v,i: i!=len(v)-1
R_before_a = lambda v,i: i+1<len(v) and v[i+1] in ("ain","aiin")
RULES=[("o",("e","ee"),R_before_d), ("y",("l",),R_not_final), ("d",("k",),R_before_a)]

def coverage(rules, label, verbose=True):
    gen=set()
    for w,g in GA.items():
        for v in apply_rules(g, rules): gen.add("".join(v))
    hit=gen & SB
    newhit=(gen-SA) & SB              # то, что добавили именно правила
    tokB=sum(cB[w] for w in hit); tokall=sum(cB.values())
    base=SA & SB
    if verbose:
        print(f"  {label}")
        print(f"     порождено форм: {len(gen):6d} (из {len(SA)} слов языка A)")
        print(f"     покрыто словаря B: {len(hit)/len(SB):6.1%} ({len(hit)}/{len(SB)})   "
              f"было без правил {len(base)/len(SB):.1%}")
        print(f"     прирост: {(len(hit)-len(base))/len(SB):+.1%}   "
              f"по токенам B покрыто {tokB/tokall:.1%}")
    return len(hit)-len(base), len(gen)-len(SA)

print("="*80); print("ОБРАЩЕНИЕ ПРАВИЛ A→B: сколько словаря B порождается из словаря A"); print("="*80)
real_gain, real_forms = coverage(RULES, "ТРИ НАЙДЕННЫХ ПРАВИЛА")
print()
for i,(nm,rs) in enumerate((("только o→e/ee перед d,dy",[RULES[0]]),
                            ("только y→l не в конце",   [RULES[1]]),
                            ("только d→k перед ain,aiin",[RULES[2]]))):
    coverage(rs, nm)
    print()

print("="*80); print("КОНТРОЛЬ: случайные правила той же формы (60 наборов по три)"); print("="*80)
GS=[g for g,n in collections.Counter(x for w in SA for x in GA[w]).most_common(18)]
rnd=random.Random(4); gains=[]; forms=[]
CONDS=[("перед d,dy",R_before_d), ("не в конце",R_not_final), ("перед ain,aiin",R_before_a),
       ("в начале", lambda v,i: i==0), ("перед o", lambda v,i: i+1<len(v) and v[i+1]=="o")]
for _ in range(60):
    rs=[]
    for _ in range(3):
        s=rnd.choice(GS); d=rnd.choice([g for g in GS if g!=s]); c=rnd.choice(CONDS)[1]
        rs.append((s,(d,),c))
    g_,f_=coverage(rs, "", verbose=False); gains.append(g_); forms.append(f_)
gains.sort()
print(f"  прирост покрытия у случайных наборов: медиана {gains[30]}, "
      f"95-й процентиль {gains[57]}, максимум {gains[-1]}")
print(f"  прирост у найденных правил: {real_gain}")
print(f"  → {'ВЫШЕ случайного потолка ✓' if real_gain>gains[57] else 'в пределах случайного ·'}")
print(f"  (порождённых новых форм: у найденных {real_forms}, у случайных в среднем "
      f"{sum(forms)/len(forms):.0f} — сравнимо, так что дело не в объёме перебора)")
