import urllib.request, json, re, base64
def api(u):
    r=urllib.request.Request(u, headers={"User-Agent":"research/1.0","Accept":"application/vnd.github+json"})
    return json.load(urllib.request.urlopen(r, timeout=30))
def raw(u):
    r=urllib.request.Request(u, headers={"User-Agent":"research/1.0"})
    return urllib.request.urlopen(r, timeout=30).read().decode("utf-8","replace")
tree=api("https://api.github.com/repos/josquin-research-project/jrp-scores/git/trees/master?recursive=1")
krn=[t["path"] for t in tree.get("tree",[]) if t["path"].endswith(".krn")]
print(f"  файлов .krn в репозитории: {len(krn)}")
# берём композиторов XV века: Ock (Окегем), Bus (Бюнуа), Duf (Дюфаи), Jos (Жоскен)
early=[p for p in krn if re.search(r"/(Ock|Bus|Duf|Mar|Obr)", p)][:60] or krn[:60]
print(f"  берём: {len(early)}, например {early[0] if early else '—'}")
txt=[]
for p in early:
    try: txt.append(raw(f"https://raw.githubusercontent.com/josquin-research-project/jrp-scores/master/{p}"))
    except Exception: pass
    if sum(len(x) for x in txt)>700000: break
open("ref/music_kern.raw","w").write("\n".join(txt))
print(f"  скачано: {sum(len(x) for x in txt):,} знаков из {len(txt)} файлов")
