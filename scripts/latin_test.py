import json, collections, math, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
VLINES=[[w for w in r["words"] if '?' not in w] for r in rows if r["locus"]=="P"]
VLINES=[l for l in VLINES if len(l)>=3]
LINELENS=[len(l) for l in VLINES]
NTOK=sum(LINELENS)
lat=open("ref/latin.clean").read().split()[:NTOK]
LAT=[]; k=0
for n in LINELENS:
    if k+n>len(lat): break
    LAT.append(lat[k:k+n]); k+=n
LATW=[w for l in LAT for w in l]
print(f"латынь: строк {len(LAT)}, слов {len(LATW)}")
T=metrics.all_metrics(LATW, LAT)
print("\nЦЕЛЕВЫЕ ВЕЛИЧИНЫ ЛАТЫНИ")
for k_,v in T.items(): print(f"   {k_:16s} {v: .4f}")
json.dump(T, open("target_lat.json","w"))

def build(items, p_rep, p_mut, line_layer=True, copy_layer=True, seed=1):
    rnd=random.Random(seed)
    s=" ".join(items); tr=collections.defaultdict(list)
    for i in range(len(s)-2): tr[s[i:i+2]].append(s[i+2])
    starts=[w[0] for w in items]
    def fresh():
        cur=" "+rnd.choice(starts); buf=[cur[1]]
        for _ in range(40):
            nx=rnd.choice(tr.get(cur) or [" "])
            if nx==" ": break
            buf.append(nx); cur=cur[1]+nx
        return "".join(buf) or "a"
    alpha=collections.Counter(c for x in items for c in x)
    AK=list(alpha); AW=list(alpha.values())
    def mutate(w):
        if not w: return "a"
        i=rnd.randrange(len(w)); op=rnd.random()
        ch=rnd.choices(AK,weights=AW)[0]
        if op<0.45: return w[:i]+ch+w[i+1:]
        if op<0.75: return w[:i]+ch+w[i:]
        return (w[:i]+w[i+1:]) or "a"
    fi=collections.Counter(l[0][0] for l in LAT); fk=list(fi); fw=[fi[x] for x in fk]
    out=[]; prev=None
    for n in LINELENS[:len(LAT)]:
        line=[]
        for j in range(n):
            if j==0 and line_layer:
                want=rnd.choices(fk,fw)[0]; w=None
                for _ in range(40):
                    c=fresh()
                    if c[0]==want: w=c; break
                w=w or (want+fresh()[1:])
            elif copy_layer and prev and rnd.random()<p_rep: w=prev
            elif copy_layer and prev and rnd.random()<p_mut: w=mutate(prev)
            else: w=fresh()
            line.append(w); prev=w
        out.append(line)
    return out

# настройка теми же двумя показателями, что и у Войнича
best=None
for pr in [0.0,0.004,0.012]:
    for pm in [0.0,0.03,0.09]:
        L=build(LATW,pr,pm); ws=[w for l in L for w in l]
        m=metrics.all_metrics(ws,L)
        e=abs(m['rep_ratio']-T['rep_ratio'])/max(T['rep_ratio'],1e-6)+abs(m['ed1']-T['ed1'])/max(T['ed1'],1e-6)
        if best is None or e<best[0]: best=(e,pr,pm,m)
_,PR,PM,mL=best
print(f"\nмодель настроена на латыни: p_rep={PR}  p_mut={PM}")
KEYS=[("mean_len","ср.длина"),("h1","h1"),("cv","CV длин"),("h2","h2"),("h2_merged","h2 склеен"),
      ("mi_pos","слотовость"),("mi_pos_merged","слот. склеен"),("rep_ratio","повторы ×"),
      ("ed1","отл. в 1 знак"),("ttr","TTR"),("hapax","хапаксы"),("wh2","H(слово|пред)"),
      ("zipf","наклон Ципфа"),("line_div","эффект строки")]
print("\n"+"="*76)
print("ТРЁХСЛОЙНАЯ МОДЕЛЬ, ОБУЧЕННАЯ НА ЛАТЫНИ, ПРОТИВ САМОЙ ЛАТЫНИ")
print("="*76)
print(f"  {'показатель':17s} {'ЛАТЫНЬ':>10s} {'модель':>10s} {'откл.':>9s}")
hits=0
for k_,lab in KEYS:
    a,b=T[k_],mL[k_]; e=abs(b-a)/max(abs(a),1e-9)
    ok = e<=0.15; hits+=ok
    print(f"  {lab:17s} {a:10.3f} {b:10.3f} {e:8.0%} {'✓' if ok else '✗'}")
print(f"\n  ПОПАДАНИЙ: {hits} из 14   (на Войниче та же модель давала 11 из 14)")
