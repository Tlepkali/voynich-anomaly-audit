import json, math, collections
D = json.load(open("parsed.json")); rows, pages = D["rows"], D["pages"]
voy = [w for r in rows for w in r["words"] if '?' not in w]
lat = open("ref/latin.clean").read().split()[:len(voy)]
eng = open("ref/english.clean").read().split()[:len(voy)]

def h(seq_of_units):
    """энтропия по последовательности единиц (символов ИЛИ слов), пробел как единица"""
    uni = collections.Counter(seq_of_units); T = len(seq_of_units)
    h1 = -sum(n/T*math.log2(n/T) for n in uni.values())
    bi = collections.Counter(zip(seq_of_units, seq_of_units[1:])); M = sum(bi.values())
    h2 = -sum(n/M*math.log2(n/M) for n in bi.values()) - h1
    return len(uni), h1, h2

def chars(words): 
    out=[]
    for w in words: out.extend(list(w)); out.append(" ")
    return out

# «склейка» устоявшихся EVA-сочетаний в одиночные знаки
MULTI = ["cfhaiin","ckhaiin","cthaiin","cphaiin","cfh","ckh","cth","cph","sh","ch",
         "iiin","iin","ii","eee","ee","aiin","ain","aiir","air","qo","dy","al","ar","ol","or"]
def merge(w):
    out, i = [], 0
    while i < len(w):
        for m in MULTI:
            if w.startswith(m, i): out.append(m); i += len(m); break
        else: out.append(w[i]); i += 1
    return out
def chars_merged(words):
    out=[]
    for w in words: out.extend(merge(w)); out.append(" ")
    return out

print("ПО СИМВОЛАМ (как в транскрипции)")
for name, ws in (("Войнич",voy),("латынь",lat),("английский",eng)):
    a,h1,h2 = h(chars(ws)); print(f"  {name:22s} алф {a:4d}  h1 {h1:5.2f}  h2 {h2:5.2f}")

print("\nПО СИМВОЛАМ, склеив частые сочетания (ch, sh, cth, aiin, qo, ee, …)")
a,h1,h2 = h(chars_merged(voy)); print(f"  {'Войнич':22s} алф {a:4d}  h1 {h1:5.2f}  h2 {h2:5.2f}")

print("\nПО СЛОВАМ — не зависит от того, как поделён алфавит")
for name, ws in (("Войнич",voy),("Войнич A",[w for r in rows for w in r['words'] if '?' not in w and pages.get(r['page'],{}).get('L')=='A']),
                 ("Войнич B",[w for r in rows for w in r['words'] if '?' not in w and pages.get(r['page'],{}).get('L')=='B']),
                 ("латынь",lat),("английский",eng)):
    ws = ws[:len(voy)]
    a,h1,h2 = h(ws)
    print(f"  {name:22s} словарь {a:6d}  H(слово) {h1:5.2f}  H(слово|пред.) {h2:5.2f}  падение {h1-h2:4.2f}")
