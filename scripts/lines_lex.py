import json, collections, random, os, sys
sys.path.insert(0,".")
D=json.load(open("parsed.json")); rows=D["rows"]; pages=D["pages"]
P=[r for r in rows if r["locus"]=="P"]
LINES=[]
for r in P:
    ws=[w for w in r["words"] if '?' not in w]
    if len(ws)>=3: LINES.append({"w":ws,"page":r["page"],"n":r["line"]})
print("="*92); print("ПОВТОРЯЮТСЯ ЛИ СТРОКИ ЦЕЛИКОМ"); print("="*92)
key=[" ".join(l["w"]) for l in LINES]
c=collections.Counter(key)
dup=[(k,v) for k,v in c.items() if v>1]
print(f"  строк: {len(LINES)}, полностью совпадающих пар: {sum(v-1 for _,v in dup)}")
for k,v in sorted(dup, key=lambda kv:-kv[1])[:5]:
    print(f"     ×{v}: {k[:80]}")
def sim(a,b):
    sa,sb=set(a),set(b)
    return len(sa&sb)/max(1,min(len(sa),len(sb)))
adj=[]; rnd=random.Random(3); ctl=[]
byp=collections.defaultdict(list)
for l in LINES: byp[l["page"]].append(l)
for pg,ls in byp.items():
    ls.sort(key=lambda x:x["n"])
    for i in range(len(ls)-1):
        if ls[i+1]["n"]==ls[i]["n"]+1: adj.append(sim(ls[i]["w"], ls[i+1]["w"]))
for _ in range(6000):
    a,b=rnd.choice(LINES), rnd.choice(LINES)
    if a is not b: ctl.append(sim(a["w"],b["w"]))
m=lambda x: sum(x)/len(x)
print(f"\n  доля общих слов у СОСЕДНИХ строк: {m(adj):.4f}  (пар {len(adj)})")
print(f"  у случайных пар строк:            {m(ctl):.4f}")
print(f"  отношение: {m(adj)/m(ctl):.2f}×")
hi=sorted(range(len(adj)), key=lambda i:-adj[i])[:3]
print(f"  максимум сходства соседних строк: {max(adj):.2f}")
print("\n  почти совпадающие соседние строки (сходство > 0,7):")
k=0
for pg,ls in byp.items():
    ls.sort(key=lambda x:x["n"])
    for i in range(len(ls)-1):
        if ls[i+1]["n"]==ls[i]["n"]+1 and sim(ls[i]["w"],ls[i+1]["w"])>0.7:
            k+=1
            if k<=3:
                print(f"     {pg} стр.{ls[i]['n']}: {' '.join(ls[i]['w'][:9])}")
                print(f"     {pg} стр.{ls[i+1]['n']}: {' '.join(ls[i+1]['w'][:9])}")
print(f"     всего таких пар: {k}")

print("\n"+"="*92)
print("СЛОВАРНЫЕ СОВПАДЕНИЯ: встречаются ли слова рукописи как настоящие слова")
print("="*92)
VOY=[w for l in LINES for w in l["w"]]
types=set(VOY)
LAT=[("латынь","ref/latin.clean"),("английский","ref/english.clean"),
     ("итальянский","ref/wiki_it.clean"),("немецкий","ref/wiki_de.clean"),
     ("турецкий","ref/wiki_tr.clean"),("баскский","ref/wiki_eu.clean"),
     ("финский","ref/wiki_fi.clean"),("Апиций","ref/g_apicius.clean"),
     ("травник Калпепера","ref/g_herbal.clean"),("Вульгата","ref/scr_vulgata.clean")]
# контроль: перемешиваем буквы внутри каждого слова рукописи
rnd=random.Random(11)
def scramble(w):
    l=list(w); rnd.shuffle(l); return "".join(l)
ctl_types=[set(scramble(w) for w in types) for _ in range(5)]
print(f"  {'язык':22s} {'словарь':>8s} {'совпало':>8s} {'доля':>7s} {'контроль':>9s} {'превышение':>11s}")
for lab,path in LAT:
    if not os.path.exists(path): continue
    voc=set(open(path).read().split())
    hit=len(types & voc)
    cm=sum(len(ct & voc) for ct in ctl_types)/len(ctl_types)
    print(f"  {lab:22s} {len(voc):8d} {hit:8d} {hit/len(types):7.2%} {cm:9.1f} "
          f"{(hit/cm if cm else float('inf')):10.2f}×")
print(f"\n  всего типов в рукописи: {len(types)}")
ex=sorted(types & set(open("ref/latin.clean").read().split()))[:14]
print(f"  примеры совпадений с латынью: {', '.join(ex)}")
