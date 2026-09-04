# -*- coding: utf-8 -*-
"""СВЕРКА СТАТЕЙ С ПЕРЕСЧИТАННЫМ. Читает data/paper_numbers.json (его пишет
scripts/paper_numbers.py) и проверяет, что каждое несущее число стоит в тексте
статьи в том виде, в каком его даёт канонический измеритель.

Плюс структурные проверки, которых числовая сверка не берёт: сходятся ли
счётчики вердиктов с инвентарём, совпадает ли число строк приложения,
не осталось ли висячих ссылок на разделы слитого черновика.

    python3 scripts/check_paper.py

Код возврата 1, если есть хоть одно расхождение.
"""
import sys, os, re, json, collections
sys.path.insert(0, "scripts")

FAIL = 0
def bad(msg):
    global FAIL; FAIL += 1; print("  ✗ " + msg)
def ok(msg):
    print("  · " + msg)

NUM_RE = re.compile(r"[−+-]?\d[\d,]*(?:\.\d+)?")

def parse_num(s):
    s = s.replace("−", "-").replace(",", "")
    try: return float(s)
    except ValueError: return None

def tolerance(fmt):
    """Полразряда последнего печатаемого знака: 0,194 сходится с 0,1935."""
    m = re.search(r"\.(\d+)f", fmt)
    if m: return 0.51 * 10 ** (-int(m.group(1)))   # 0,51 а не 0,5: ровная половина иначе не сходится
    return 0.51

print("=" * 78); print("1. НЕСУЩИЕ ЧИСЛА"); print("=" * 78)
if not os.path.exists("data/paper_numbers.json"):
    print("  data/paper_numbers.json нет — сперва: python3 scripts/paper_numbers.py")
    sys.exit(2)
NUMS = json.load(open("data/paper_numbers.json", encoding="utf-8"))
TXT = {p: open(p, encoding="utf-8").read() for p in {r["paper"] for r in NUMS}}
found = 0
for r in NUMS:
    t = TXT[r["paper"]]; v = r["value"]; tol = tolerance(r["fmt"])
    shown = r["fmt"].format(v)
    if r["context"]:
        wins = [t[max(0, m.start() - 500):m.end() + 500] for m in re.finditer(re.escape(r["context"]), t)]
        if not wins:
            bad(f"{r['key']}: контекст «{r['context'][:44]}» в {r['paper']} не найден вовсе"); continue
        pool = " ".join(wins); scope = f"рядом с «{r['context'][:34]}»"
    else:
        pool = t; scope = "в тексте"
    cands = [parse_num(x) for x in NUM_RE.findall(pool)]
    hit = any(c is not None and abs(c - v) <= tol for c in cands)
    if hit:
        found += 1
    else:
        near = sorted((c for c in cands if c is not None and abs(c - v) <= max(tol * 20, abs(v) * 0.5)),
                      key=lambda c: abs(c - v))[:3]
        bad(f"{r['key']}: пересчёт даёт {shown}, {scope} такого нет"
            + (f" (ближайшее: {', '.join(str(x) for x in near)})" if near else ""))
ok(f"сошлось {found} из {len(NUMS)}")

# ── ПОКРЫТИЕ: сколько чисел текста РЕАЛЬНО сопоставлены с пересчитанным ────
# «внутри окна» покрытием не считается: число покрыто, только если какая-то
# запись манифеста даёт ровно его, и её контекст стоит рядом.
for paper in sorted(TXT):
    t = TXT[paper]
    body = t[:t.index("## Appendix")] if "## Appendix" in t else t
    anchors = []
    for r in NUMS:
        if r["paper"] != paper or not r["context"]: continue
        for m in re.finditer(re.escape(r["context"]), body):
            anchors.append((max(0, m.start() - 500), m.end() + 500, r["value"], tolerance(r["fmt"])))
    total = seen = 0
    for m in NUM_RE.finditer(body):
        v = parse_num(m.group(0))
        if v is None or abs(v) < 1e-9: continue
        total += 1
        if any(a <= m.start() <= b and abs(v - val) <= tol for a, b, val, tol in anchors): seen += 1
    pct = 100 * seen / max(total, 1)
    ok(f"{paper}: пересчётом покрыто {seen} из {total} чисел текста ({pct:.0f} %)")
print("  · остальные — производные (отношения, проценты от цели), числа из чужих")
print("    работ и величины, посчитанные скриптами вне манифеста")

print("=" * 78); print("2. СЧЁТЧИКИ ПРОТИВ ИНВЕНТАРЯ"); print("=" * 78)
from inventory import INV
WORD = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",
        10:"ten",15:"fifteen",18:"eighteen",19:"nineteen",21:"twenty-one",22:"twenty-two",
        23:"twenty-three",29:"twenty-nine",35:"thirty-five",37:"thirty-seven",
        50:"fifty",52:"fifty-two",70:"seventy"}
for paper, pred, name in [("paper-audit.md", lambda d: not d["id"].startswith("G"), "аудит"),
                          ("paper-generator.md", lambda d: d["id"].startswith("G"), "генеративная")]:
    S = [d for d in INV if pred(d)]
    t = open(paper, encoding="utf-8").read()
    rows = len(re.findall(r"^\| [A-G]\d", t, re.M))
    if rows != len(S): bad(f"{name}: строк приложения {rows}, записей в инвентаре {len(S)}")
    else: ok(f"{name}: приложение и инвентарь по {rows} строк")
    c = collections.Counter(d["verdict"] for d in S)
    if sum(c.values()) != len(S): bad(f"{name}: вердикты не покрывают все записи")
    for verdict, label in [("CONFIRM", "устояло"), ("DISSOLVE", "растворилось"),
                           ("WEAK", "ослаблено"), ("RETRACT", "отозвано")]:
        w = WORD.get(c[verdict])
        if w and not re.search(rf"\b{w}\b", t, re.I):
            bad(f"{name}: {label} {c[verdict]} ({w}) — этого слова в тексте нет, счётчик мог устареть")
    # разметка вердикта в приложении против инвентаря
    MARK = {"CONFIRM": "survives", "DISSOLVE": "dissolves", "WEAK": "weakened",
            "ATTRIB": "attributed", "RETRACT": "retracted"}
    for d in S:
        m = re.search(rf"^\| {re.escape(d['id'])} \|.*$", t, re.M)
        if not m: bad(f"{name}: записи {d['id']} нет в приложении")
        elif MARK[d["verdict"]] not in m.group(0):
            bad(f"{name}: {d['id']} в инвентаре {d['verdict']}, в приложении иначе")

print("=" * 78); print("3. АТРИБУЦИЯ: ЧЬЁ УТВЕРЖДЕНИЕ"); print("=" * 78)
# Заведено 04.09.2026. Раздел 2 сличал приложение с инвентарём построчно и
# повердиктно, но колонку «чьё» не сравнивал ВОВСЕ. Из-за этого пять
# переатрибуций после разбора приор-арта легли в inventory.py и не доехали до
# статей: B7 и C2 месяц стояли как «ours», хотя B7 — Карриер 1976 и Редди с
# Найтом 2011, а C2 — сообщество. Статья присваивала чужое ровно там, где
# чтение это и должно было убрать. Нашлось руками, а не прогоном.
#
# Инвентарь по-русски, приложения по-английски, поэтому сверяются две вещи:
#   * ФЛАГ «своё» — \bнаш(е|а|и)\b против \bour. Граница слова обязательна:
#     без неё «до наших дней» читается как притязание (ловилось на D11).
#   * ИМЕНА — те, что несут атрибуцию: при имени стоит год либо оно идёт от
#     «сводка». Прочие упоминания выводятся отдельно как мягкие: имя внутри
#     описательного оборота источником не является, но и молча пропадать не
#     должно.
# Незнакомые имена печатаются списком — иначе карта тихо перестанет покрывать
# новые записи, и проверка выродится, оставаясь зелёной.
NAMES = {"Зандберген":"Zandbergen","Карриер":"Currier","Стольфи":"Stolfi","Грешко":"Greshko",
 "Тилтман":"Tiltman","Редди":"Reddy","Шиннер":"Schinner","Боуэрн":"Bowern","Пеллинг":"Pelling",
 "Заттер":"Zattera","Найт":"Knight","Беннетт":"Bennett","Ландини":"Landini","Смит":"Smith",
 "Паризель":"Parisel","Нил":"Neal","Линдеманн":"Lindemann","Чам":"Cham","Тимм":"Timm",
 "Сазонов":"Sazonov","Понци":"Ponzi","Джексон":"Jackson","Монтемурро":"Montemurro",
 "Занетте":"Zanette","Матлах":"Matlach","Гаскелл":"Gaskell","Стернек":"Sterneck",
 "Полиш":"Polish","Рагг":"Rugg","Ньюболд":"Newbold"}
NOT_A_NAME = {"Брайан", "Дэвид", "Марко"}          # имена, фамилии рядом в карте
OWN = re.compile(r"\bнаш(?:е|а|и|его|ей|ем)\b")

CELL = {}
for _p in ("paper-audit.md", "paper-generator.md"):
    for _ln in open(_p, encoding="utf-8"):
        if re.match(r"^\| [A-G]\d", _ln):
            _f = _ln.split("|")
            if len(_f) > 4: CELL[_f[1].strip()] = _f[3].strip()

soft, unmapped, checked = [], set(), 0
for d in INV:
    ru, en = d["whose"], CELL.get(d["id"])
    if en is None: continue                        # отсутствие строки ловит раздел 2
    checked += 1
    if bool(OWN.search(ru.lower())) != bool(re.search(r"\bour", en.lower())):
        bad(f"{d['id']}: флаг «своё» расходится — инв «{ru[:44]}», статья «{en[:44]}»")
    for stem, lat in NAMES.items():
        m = re.search(stem, ru)
        if not m or lat.lower() in en.lower(): continue
        is_src = bool(re.search(r"\d{4}", ru[m.end():m.end() + 14])) or \
                 "свод" in ru[max(0, m.start() - 12):m.start()].lower()
        if is_src: bad(f"{d['id']}: {lat} значится источником в инвентаре, но не в статье")
        else: soft.append(f"{d['id']}: {lat} упомянут в инвентаре без года — «{en[:44]}»")
    for tok in re.findall(r"[А-ЯЁ][а-яё]{2,}", ru):
        if tok in NOT_A_NAME: continue
        if not any(tok.startswith(k) or k.startswith(tok) for k in NAMES): unmapped.add(tok)
ok(f"атрибуция сверена по {checked} строкам: флаг «своё» и {len(NAMES)} имён")
for x in soft: print(f"  ~ {x}")
if unmapped:
    print(f"  ~ не в карте имён (дополнить NAMES, если это фамилии): {', '.join(sorted(unmapped))}")

print("=" * 78); print("4. ССЫЛКИ И ОСТАТКИ РАЗДЕЛЕНИЯ"); print("=" * 78)
for paper in ("paper-audit.md", "paper-generator.md"):
    t = open(paper, encoding="utf-8").read()
    secs = set(re.findall(r"^## (\d+[a-z]?)\.", t, re.M)) | set(re.findall(r"^### (\d+\.\d+)", t, re.M))
    for m in re.finditer(r"§\s?(\d+)(?:\.(\d+))?", t):
        n, sub = m.group(1), m.group(2)
        ctx = t[max(0, m.start() - 60):m.start()]
        if "companion" in ctx.lower(): continue      # ссылка в другую статью
        ref = f"{n}.{sub}" if sub else n
        if ref not in secs: bad(f"{paper}: ссылка §{ref}, а такого раздела нет")
    if "paper-draft" in t: bad(f"{paper}: упоминание paper-draft — имя из прошлой версии")
ok("ссылки проверены")

print("=" * 78)
print("РАСХОЖДЕНИЙ: " + (str(FAIL) if FAIL else "нет"))
sys.exit(1 if FAIL else 0)
