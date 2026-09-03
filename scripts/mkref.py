import re, glob, unicodedata

def strip_html(h):
    h = re.sub(r'(?is)<(script|style).*?</\1>', ' ', h)
    h = re.sub(r'(?s)<[^>]+>', ' ', h)
    h = re.sub(r'&[a-zA-Z]+;|&#\d+;', ' ', h)
    return h

def normalize(t):
    t = unicodedata.normalize('NFKD', t)
    t = ''.join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r'[^a-z]+', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

lat = " ".join(normalize(strip_html(open(f, encoding='utf-8', errors='replace').read()))
               for f in sorted(glob.glob("ref/pliny.nh*.html")))
open("ref/latin.clean","w").write(lat)

eng = open("ref/english.txt", encoding='utf-8', errors='replace').read()
eng = eng.split("*** START")[-1].split("*** END")[0]
open("ref/english.clean","w").write(normalize(eng))

for n in ("latin","english"):
    t = open(f"ref/{n}.clean").read()
    print(f"{n:10s} {len(t):>9,} символов, {len(t.split()):>8,} слов")
