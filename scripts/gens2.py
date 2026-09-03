import random, collections, json, sys
sys.path.insert(0,".")
import gens
VOY, LINELENS, LINES = gens.VOY, gens.LINELENS, gens.LINES

# ── A2: решётка с большой таблицей, фрагменты извлечены из рукописи (как делал Рагг)
def build_big_tables(nP=26, nM=26, nS=30):
    beg=collections.Counter(); end=collections.Counter(); mid=collections.Counter()
    for w in VOY:
        for k in (1,2,3):
            if len(w)>k: beg[w[:k]]+=1; end[w[-k:]]+=1
        if len(w)>4: mid[w[2:-2]]+=1
    P=[x for x,_ in beg.most_common(nP)]; S=[x for x,_ in end.most_common(nS)]
    M=['']+[x for x,_ in mid.most_common(nM-1)]
    return P,M,S
BP,BM,BS = build_big_tables()

def gen_slot_big(p_mid=0.6, seed=1):
    rnd=random.Random(seed); out=[]
    for n in LINELENS:
        line=[]
        for _ in range(n):
            w=rnd.choice(BP)
            if rnd.random()<p_mid: w+=rnd.choice(BM)
            w+=rnd.choice(BS)
            line.append(w or 'o')
        out.append(line)
    return out

# ── E: три слоя — марковская форма + копирование слов + осведомлённость о строке
def gen_composite(p_rep, p_mut, seed=1):
    rnd=random.Random(seed)
    s=" ".join(VOY)
    tr=collections.defaultdict(list)
    for i in range(len(s)-2): tr[s[i:i+2]].append(s[i+2])
    def fresh():
        cur=" "+rnd.choice("oqcdstkyp"); buf=[cur[1]]
        for _ in range(40):
            nxt=rnd.choice(tr.get(cur) or [" "])
            if nxt==" ": break
            buf.append(nxt); cur=cur[1]+nxt
        return "".join(buf) or "o"
    # распределение первых букв в начале строки — единственная «подсмотренная» деталь слоя 3
    fi=collections.Counter(l[0][0] for l in LINES if l)
    fk=list(fi); fw=[fi[k] for k in fk]
    out=[]; prev=None
    for n in LINELENS:
        line=[]
        for j in range(n):
            if j==0:
                want=rnd.choices(fk,fw)[0]
                w=None
                for _ in range(40):
                    c=fresh()
                    if c[0]==want: w=c; break
                w = w or (want+fresh()[1:])
            elif prev and rnd.random()<p_rep: w=prev
            elif prev and rnd.random()<p_mut: w=gens.mutate(prev, rnd)
            else: w=fresh()
            line.append(w); prev=w
        out.append(line)
    return out
