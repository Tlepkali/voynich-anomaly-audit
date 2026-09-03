# -*- coding: utf-8 -*-
"""Общий разбор любого IVTFF-файла теми же правилами очистки, что и ZL3b."""
import re, json, sys, collections
page_re = re.compile(r'^<(f[0-9]+[rv][0-9]*)>\s*(.*)$')
line_re = re.compile(r'^<(f[0-9]+[rv][0-9]*)\.(\d+),([@+=*&])([A-Za-z])([A-Za-z0-9]?)>\s*(.*)$')
alt_re  = re.compile(r'\[([^\]]*)\]')
def clean(t):
    t = re.sub(r'<[^>]*>', '', t)
    t = re.sub(r'\{[^}]*\}', '', t)
    t = alt_re.sub(lambda m: m.group(1).split(':')[0], t)
    t = re.sub(r'@\d+;', '', t)
    t = t.replace("'", '').replace('!', '').replace('%', '')
    t = t.replace(',', '.')
    t = re.sub(r'[-=~/]', '', t)
    return t
def parse(src):
    pages={}; rows=[]; cur=None; seen=set()
    for raw in open(src, encoding='utf-8', errors='replace'):
        raw=raw.rstrip('\n')
        m=page_re.match(raw)
        if m:
            cur=m.group(1); pages[cur]=dict(re.findall(r'\$([A-Z])=([A-Za-z0-9])', m.group(2))); continue
        m=line_re.match(raw)
        if m:
            pg,ln,pm,lt,sub,txt=m.groups()
            key=(pg,int(ln),lt,sub)
            if key in seen: continue          # RF1b-e повторяет строки — берём первую
            seen.add(key)
            ws=[w for w in clean(txt).split('.') if w]
            if ws: rows.append(dict(page=pg,line=int(ln),pos=pm,locus=lt,sub=sub,words=ws))
    return dict(pages=pages, rows=rows)
if __name__=="__main__":
    for name in sys.argv[1:]:
        d=parse(f"data/{name}.txt")
        json.dump(d, open(f"data/parsed_{name}.json","w"))
        P=[r for r in d["rows"] if r["locus"]=="P"]
        f=[w for r in P for w in r["words"] if '?' not in w]
        ch=collections.Counter(c for w in f for c in w)
        print(f"  {name:>10s}: строк {len(d['rows']):5d}, локус P {len(f):6d} токенов, "
              f"{len(set(f)):5d} типов, алфавит {len(ch):2d} знаков, "
              f"ср.длина {sum(len(w) for w in f)/max(len(f),1):.2f}, страниц {len(d['pages'])}")
