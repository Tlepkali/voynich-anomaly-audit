import json, math, collections, random
random.seed(7)
D = json.load(open("parsed.json")); rows, pages = D["rows"], D["pages"]
voy = [w for r in rows for w in r["words"] if '?' not in w]
N = len(voy)

def metrics(words):
    words = words[:N]
    text = " ".join(words)
    uni = collections.Counter(text); T = len(text)
    h1 = -sum(n/T*math.log2(n/T) for n in uni.values())
    bi = collections.Counter(text[i:i+2] for i in range(T-1)); M = sum(bi.values())
    h2 = -sum(n/M*math.log2(n/M) for n in bi.values()) - h1
    ls = [len(w) for w in words]; mu = sum(ls)/len(ls)
    sd = (sum((l-mu)**2 for l in ls)/len(ls))**0.5
    ty = collections.Counter(words)
    hap = sum(1 for w,n in ty.items() if n==1)/len(ty)
    return dict(alpha=len(uni), h0=math.log2(len(uni)), h1=h1, h2=h2,
                mu=mu, sd=sd, cv=sd/mu, ttr=len(ty)/len(words), hapax=hap)

VOWELS = set("aeiou")
lat = open("ref/latin.clean").read().split()
eng = open("ref/english.clean").read().split()
abjad = [ "".join(c for c in w if c not in VOWELS) or "x" for w in lat ]
# «многословный» шифр: каждая буква -> пара символов из 6-символьного алфавита
sym = "cdehko"; pairs = [a+b for a in sym for b in sym]
vmap = {ch: pairs[i] for i, ch in enumerate("abcdefghijklmnopqrstuvwxyz")}
verbose = [ "".join(vmap[c] for c in w) for w in lat ]
# контроль: слова, собранные из позиционных «слотов» (как слотовая грамматика)
slots = [["q","o","ch","sh","d"],["k","t","p","f","o","e"],["e","a","o",""],["ee","dy","in","y","l","r","n"]]
gen = ["".join(random.choice(s) for s in slots) for _ in range(N)]

corpora = [("Войнич (весь)", voy),
           ("Войнич — Карриер A", [w for r in rows for w in r["words"] if '?' not in w and pages.get(r["page"],{}).get("L")=="A"]),
           ("Войнич — Карриер B", [w for r in rows for w in r["words"] if '?' not in w and pages.get(r["page"],{}).get("L")=="B"]),
           ("латынь (Плиний)", lat),
           ("английский", eng),
           ("латынь без гласных", abjad),
           ("латынь, verbose-шифр", verbose),
           ("генератор по слотам", gen)]

print(f"{'корпус':24s} {'алф':>4s} {'h1':>5s} {'h2':>5s} {'ср.дл':>6s} {'ст.от':>6s} {'CV':>5s} {'TTR':>5s} {'хапакс':>7s}")
print("-"*76)
for name, w in corpora:
    if len(w) < 5000: continue
    m = metrics(w)
    print(f"{name:24s} {m['alpha']:4d} {m['h1']:5.2f} {m['h2']:5.2f} {m['mu']:6.2f} {m['sd']:6.2f} {m['cv']:5.2f} {m['ttr']:5.3f} {m['hapax']:6.0%}")
