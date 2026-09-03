import re, json, collections

SRC = "ZL3b-n.txt"
pages = {}          # page -> metadata dict
rows  = []          # (page, line_no, pos_marker, locus_type, [words])

cur_page, cur_meta = None, {}
page_re  = re.compile(r'^<(f[0-9]+[rv][0-9]*)>\s*(.*)$')
line_re  = re.compile(r'^<(f[0-9]+[rv][0-9]*)\.(\d+),([@+=*&])([A-Za-z])([A-Za-z0-9]?)>\s*(.*)$')
alt_re   = re.compile(r'\[([^\]]*)\]')

def clean(t):
    t = re.sub(r'<[^>]*>', '', t)            # разметка и комментарии в угловых скобках
    t = re.sub(r'\{[^}]*\}', '', t)          # инлайновые комментарии в фигурных
    t = alt_re.sub(lambda m: m.group(1).split(':')[0], t)   # [a:b] -> a (чтение первого транскриптора)
    t = re.sub(r'@\d+;', '', t)             # ссылки на спецсимволы
    t = t.replace("'", '')
    t = t.replace('!', '').replace('%', '')  # выравнивающий null и «нечитаемый фрагмент»
    t = t.replace(',', '.')                  # неуверенный пробел = пробел
    t = re.sub(r'[-=~/]', '', t)
    return t

for raw in open(SRC, encoding='utf-8', errors='replace'):
    raw = raw.rstrip('\n')
    m = page_re.match(raw)
    if m:
        cur_page = m.group(1)
        cur_meta = dict(re.findall(r'\$([A-Z])=([A-Za-z0-9])', m.group(2)))
        pages[cur_page] = cur_meta
        continue
    m = line_re.match(raw)
    if m:
        page, ln, posmark, ltype, sub, text = m.groups()
        words = [w for w in clean(text).split('.') if w]
        if words:
            rows.append({"page": page, "line": int(ln), "pos": posmark,
                         "locus": ltype, "sub": sub, "words": words})

# что осталось из символов — проверка качества разбора
chars = collections.Counter(c for r in rows for w in r["words"] for c in w)
print("страниц с метаданными:", len(pages))
print("строк текста:", len(rows))
print("токенов:", sum(len(r['words']) for r in rows))
print("\nсимволы после очистки:")
for c, n in chars.most_common():
    print(f"   {c!r:5s} {n:6d}")
json.dump({"pages": pages, "rows": rows}, open("parsed.json","w"))
