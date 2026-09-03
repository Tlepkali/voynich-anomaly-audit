import json, collections, math, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
VL=[[w for w in r["words"] if '?' not in w] for r in rows if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]; LINELENS=[len(l) for l in VL]; NTOK=sum(LINELENS)
def cut(path):
    ws=open(path).read().split()[:NTOK]; out=[];k=0
    for n in LINELENS:
        if k+n>len(ws): break
        out.append(ws[k:k+n]); k+=n
    return out
def build(items, LINES, p_rep, p_mut, seed=1):
    rnd=random.Random(seed)
    s=" ".join(items); tr=collections.defaultdict(list)
    for i in range(len(s)-2): tr[s[i:i+2]].append(s[i+2])
    starts=[w[0] for w in items]
    alpha=collections.Counter(c for x in items for c in x); AK=list(alpha); AW=list(alpha.values())
    def fresh():
        cur=" "+rnd.choice(starts); buf=[cur[1]]
        for _ in range(40):
            nx=rnd.choice(tr.get(cur) or [" "])
            if nx==" ": break
            buf.append(nx); cur=cur[1]+nx
        return "".join(buf) or "a"
    def mut(w):
        if not w: return "a"
        i=rnd.randrange(len(w)); op=rnd.random(); ch=rnd.choices(AK,weights=AW)[0]
        if op<0.45: return w[:i]+ch+w[i+1:]
        if op<0.75: return w[:i]+ch+w[i:]
        return (w[:i]+w[i+1:]) or "a"
    fi=collections.Counter(l[0][0] for l in LINES); fk=list(fi); fw=[fi[x] for x in fk]
    out=[]; prev=None
    for n in [len(l) for l in LINES]:
        line=[]
        for j in range(n):
            if j==0:
                want=rnd.choices(fk,fw)[0]; w=None
                for _ in range(40):
                    c=fresh()
                    if c[0]==want: w=c; break
                w=w or (want+fresh()[1:])
            elif prev and rnd.random()<p_rep: w=prev
            elif prev and rnd.random()<p_mut: w=mut(prev)
            else: w=fresh()
            line.append(w); prev=w
        out.append(line)
    return out
KEYS=[("mean_len","ср.длина"),("h1","h1"),("cv","CV длин"),("h2","h2"),("h2_merged","h2 склеен"),
      ("mi_pos","слотовость"),("mi_pos_merged","слот. склеен"),("rep_ratio","повторы ×"),
      ("ed1","отл. в 1 знак"),("ttr","TTR"),("hapax","хапаксы"),("wh2","H(слово|пред)"),
      ("zipf","наклон Ципфа"),("line_div","эффект строки")]
def run(path,label):
    LINES=cut(path); W=[w for l in LINES for w in l]
    T=metrics.all_metrics(W,LINES)
    best=None
    for pr in [0.0,0.004,0.012]:
        for pm in [0.0,0.03,0.09]:
            L=build(W,LINES,pr,pm); ws=[w for l in L for w in l]
            m=metrics.all_metrics(ws,L)
            e=abs(m['rep_ratio']-T['rep_ratio'])/max(T['rep_ratio'],1e-6)+abs(m['ed1']-T['ed1'])/max(T['ed1'],1e-6)
            if best is None or e<best[0]: best=(e,pr,pm,m)
    _,PR,PM,M=best
    hits=sum(1 for k,_ in KEYS if abs(M[k]-T[k])/max(abs(T[k]),1e-9)<=0.15)
    return T,M,hits,PR,PM
T,M,h,PR,PM = run("ref/english.clean","английский")
print(f"АНГЛИЙСКИЙ — модель настроена: p_rep={PR}  p_mut={PM}\n")
print(f"  {'показатель':17s} {'ЯЗЫК':>10s} {'модель':>10s} {'откл.':>9s}")
for k,lab in KEYS:
    a,b=T[k],M[k]; e=abs(b-a)/max(abs(a),1e-9)
    print(f"  {lab:17s} {a:10.3f} {b:10.3f} {e:8.0%} {'✓' if e<=0.15 else '✗'}")
print(f"\n  ПОПАДАНИЙ: {h} из 14")
json.dump({"T":T,"M":M,"hits":h}, open("eng_model.json","w"))
