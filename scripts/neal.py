# -*- coding: utf-8 -*-
import json, collections
D=json.load(open("parsed.json")); PG=D["pages"]
rows=[r for r in D["rows"] if r["locus"]=="P"]
print("Полей в строке:", sorted(rows[0].keys()))
print("Пример:", {k:v for k,v in rows[0].items() if k!="words"}, rows[0]["words"][:5])
# есть ли разметка абзацев / номера строк
ks=collections.Counter()
for r in rows[:400]:
    for k,v in r.items():
        if k!="words": ks[k]+=1
print("\nЧастоты полей:", dict(ks))
# сколько строк на страницу и как определить первую строку абзаца
byp=collections.defaultdict(list)
for r in rows: byp[r["page"]].append(r)
print("\nСтраниц со сплошным текстом:", len(byp))
p=list(byp)[0]
for r in byp[p][:4]: print("  ", {k:v for k,v in r.items() if k!="words"}, " ".join(r["words"][:6]))
