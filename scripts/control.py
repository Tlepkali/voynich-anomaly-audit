import json, math, collections
D = json.load(open("parsed.json")); rows, pages = D["rows"], D["pages"]
voy = [w for r in rows for w in r["words"] if '?' not in w]
lat = open("ref/latin.clean").read().split()[:len(voy)]

MULTI = ["cfhaiin","ckhaiin","cthaiin","cphaiin","cfh","ckh","cth","cph","sh","ch",
         "iiin","iin","ii","eee","ee","aiin","ain","aiir","air","qo","dy"]
def merge(w):
    out,i=[],0
    while i<len(w):
        for m in MULTI:
            if w.startswith(m,i): out.append(m); i+=len(m); break
        else: out.append(w[i]); i+=1
    return out

def posclass(n,i): return "один" if n==1 else ("начало" if i==0 else ("конец" if i==n-1 else "середина"))
def mi(seqs):
    j=collections.Counter()
    for u in seqs:
        for i,c in enumerate(u): j[(c,posclass(len(u),i))]+=1
    T=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (g,p),n in j.items(): pg[g]+=n; pp[p]+=n
    return sum(n/T*math.log2((n/T)/((pg[g]/T)*(pp[p]/T))) for (g,p),n in j.items())

print("КОНТРОЛЬ: сохраняется ли жёсткость позиций после склейки сочетаний?")
print(f"  Войнич, посимвольно      I = {mi([list(w) for w in voy]):.3f} бит")
print(f"  Войнич, склеенные знаки  I = {mi([merge(w) for w in voy]):.3f} бит")
print(f"  латынь (эталон)          I = {mi([list(w) for w in lat]):.3f} бит")
print(f"  латынь, склеены частые пары I = {mi([merge_lat for merge_lat in [list(w) for w in lat]]):.3f} бит  (без изменений)")

print("\nЯРЛЫКИ (подписи к рисункам) против текста абзацев")
lab = [w for r in rows if r['locus']=='L' for w in r['words'] if '?' not in w]
par = [w for r in rows if r['locus']=='P' for w in r['words'] if '?' not in w]
for name, ws in (("ярлыки", lab), ("абзацы", par)):
    if len(ws)<200: continue
    ln=[len(w) for w in ws]; mu=sum(ln)/len(ln)
    ty=collections.Counter(ws)
    print(f"  {name:8s} токенов {len(ws):6d}  типов {len(ty):5d}  TTR {len(ty)/len(ws):.3f}  ср.длина {mu:.2f}")
print("  доля ярлыков, встречающихся и в абзацах: "
      f"{sum(1 for w in set(lab) if w in set(par))/max(1,len(set(lab))):.0%}")

print("\nПОСЛЕДНЕЕ слово строки — тоже особое?")
lastw=[r['words'][-1] for r in rows if r['words'] and '?' not in r['words'][-1]]
mid  =[w for r in rows for w in r['words'][1:-1] if '?' not in w]
for name, ws in (("конец строки", lastw), ("середина строки", mid)):
    c=collections.Counter(w[-1] for w in ws); T=sum(c.values())
    top=", ".join(f"{k} {v/T:.0%}" for k,v in c.most_common(5))
    print(f"  {name:16s} последняя буква: {top}")
