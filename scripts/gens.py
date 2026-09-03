import random, collections, json, math, sys
sys.path.insert(0,".")
import metrics

D=json.load(open("parsed.json")); rows=D["rows"]
LINES=[[w for w in r["words"] if '?' not in w] for r in rows]
LINES=[l for l in LINES if l]
VOY=[w for l in LINES for w in l]
NTOK=len(VOY); LINELENS=[len(l) for l in LINES]
GLYPHS="oeyhacdikl rstnqpmfg".replace(" ","")
GW=[25143,20224,17691,17480,14521,12983,12963,11721,10825,10523,7408,7265,6798,6119,5422,1604,1053,463,151]
GW=GW[:len(GLYPHS)]

# ── таблицы в духе решётки Кардано (Rugg): приставка + середина + окончание
PRE = ['','q','o','y','d','s','ch','sh','k','t','p','f','cth','ckh','cph']
MID = ['','o','a','e','ee','ok','ot','ol','or','ke','te','che','she','od','ai']
SUF = ['y','dy','in','iin','aiin','l','r','n','ol','or','ar','al','am','ey','edy','s','o','']

def geom_w(n, alpha):
    w=[alpha**i for i in range(n)]; s=sum(w); return [x/s for x in w]

def make_tables(alpha):
    return ([PRE, geom_w(len(PRE),alpha)], [MID, geom_w(len(MID),alpha)], [SUF, geom_w(len(SUF),alpha)])

def slot_word(tb, p_mid, rnd):
    (P,pw),(M,mw),(S,sw) = tb
    w = rnd.choices(P,pw)[0]
    if rnd.random() < p_mid: w += rnd.choices(M,mw)[0]
    w += rnd.choices(S,sw)[0]
    return w or 'o'

def mutate(w, rnd):
    op = rnd.random()
    if not w: return 'o'
    i = rnd.randrange(len(w))
    if op < 0.45:  return w[:i] + rnd.choices(GLYPHS,GW)[0] + w[i+1:]
    if op < 0.75:  return w[:i] + rnd.choices(GLYPHS,GW)[0] + w[i:]
    return (w[:i] + w[i+1:]) or 'o'

def gen_slot(alpha, p_mid, seed=1):
    rnd=random.Random(seed); tb=make_tables(alpha)
    return [[slot_word(tb,p_mid,rnd) for _ in range(n)] for n in LINELENS]

def gen_selfcite(p_copy, W, alpha=0.80, p_mid=0.55, seed=1):
    rnd=random.Random(seed); tb=make_tables(alpha)
    out=[]; flat=[slot_word(tb,p_mid,rnd) for _ in range(30)]   # затравка
    for n in LINELENS:
        line=[]
        for _ in range(n):
            src = flat[-rnd.randrange(1, min(W,len(flat))+1)]
            w = src if rnd.random()<p_copy else mutate(src, rnd)
            line.append(w); flat.append(w)
        out.append(line)
    return out

def gen_hybrid(p_self, p_copy, W, alpha, p_mid, line_reset=False, seed=1):
    rnd=random.Random(seed); tb=make_tables(alpha)
    out=[]; flat=[slot_word(tb,p_mid,rnd) for _ in range(30)]
    for n in LINELENS:
        line=[]
        for j in range(n):
            fresh = (j==0 and line_reset) or rnd.random()>p_self or len(flat)<2
            if fresh: w=slot_word(tb,p_mid,rnd)
            else:
                src=flat[-rnd.randrange(1,min(W,len(flat))+1)]
                w = src if rnd.random()<p_copy else mutate(src,rnd)
            line.append(w); flat.append(w)
        out.append(line)
    return out

def gen_markov2(seed=1):
    rnd=random.Random(seed)
    s=" ".join(VOY)
    tr=collections.defaultdict(list)
    for i in range(len(s)-2): tr[s[i:i+2]].append(s[i+2])
    cur=" f"; buf=[]
    while len(buf) < len(s):
        nxt = rnd.choice(tr.get(cur) or [" "]); buf.append(nxt); cur=cur[1]+nxt
    ws=[w for w in "".join(buf).split(" ") if w]
    out=[]; k=0
    for n in LINELENS:
        out.append(ws[k:k+n]); k+=n
        if k>=len(ws): break
    return [l for l in out if l]
