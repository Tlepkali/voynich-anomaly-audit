# -*- coding: utf-8 -*-
"""ЗОДИАКАЛЬНЫЕ ПОДПИСИ: СЧЁТНАЯ ЛИ ЭТО ПОСЛЕДОВАТЕЛЬНОСТЬ.

ГИПОТЕЗА. Нимфы зодиакальных страниц пронумерованы (градус знака 1..30 либо
день). Разметка это допускает: 15 или 30 подписей на странице, кольца открыты
меткой @Lz и продолжены &Lz, углы на циферблате внутри кольца монотонны.

ГЛАВНОЕ ЗАТРУДНЕНИЕ, ИЗ-ЗА КОТОРОГО НУЖЕН ПРАВИЛЬНЫЙ НУЛЬ. Соседние слова в
рукописи похожи ВЕЗДЕ — самоцитирование её обычное поведение (записи G3, G22).
Поэтому «соседние подписи похожи» НЕ есть довод за счёт. Нуль обязан содержать
механизм, чью достаточность он проверяет (правило, которым отозвана G20).

ЧЕТЫРЕ ПРОВЕРКИ, ОБЪЯВЛЕНЫ ДО ЗАПУСКА.

  S4 ГЛАВНАЯ — СОГЛАСИЕ ПО МЕСТУ МЕЖДУ СТРАНИЦАМИ. Если подписи нумеруют,
  то седьмая нимфа одного знака и седьмая нимфа другого несут ОДНО И ТО ЖЕ
  слово. Это предсказание самоподтверждающееся: неверная гипотеза его не даёт,
  как неверное правило не даёт рифмованного двустишия. Начало отсчёта на
  странице неизвестно, поэтому берётся ЛУЧШИЙ поворот — и нуль берёт лучший
  поворот ТОЖЕ, иначе преимущество достаётся подгонке.

  S1 — ПРОФИЛЬ СХОДСТВА ПО СДВИГУ. Счёт даёт НЕмонотонный профиль: горб на
  основании системы (5, 10, 12, 15). Обычная местная повторяемость даёт
  монотонный спад. Ищем локальный максимум при сдвиге 3..15.

  S2 — БЛОЧНОСТЬ. В позиционной системе «десятки» держатся непрерывным куском.
  Мера: число серий (максимальных непрерывных кусков) на знак вдоль
  последовательности; меньше серий = блочнее.

  S3 — ДЛИНА. Складные системы (римская, палочная) растут в длину внутри блока
  и сбрасываются. Связь длины с местом и её периодичность.

НУЛИ. N1 перемешивание внутри страницы (есть ли вообще порядковая структура);
N2 СПЛОШНОЙ ТЕКСТ ТЕХ ЖЕ СТРАНИЦ, нарезанный отрезками той же длины — он
СОДЕРЖИТ местную повторяемость рукописи и потому решает дело; N3 подписи
других разделов (аптечный, астрономия) в их порядке — контроль на «подписи это
другой регистр».

КРИТЕРИЙ, НАЗНАЧЕН ЗДЕСЬ И ДО ПЕРВОГО ЗАПУСКА. Счёт считается показанным,
только если S4 проходит при p < 0,01, ЛИБО S1 и S2 обе проходят при p < 0,01
против ОБОИХ нулей N2 и N3. Иначе итог отрицательный, и пятой проверки не
будет: перебирать признаки, пока один не выстрелит, — та самая ошибка, из-за
которой отозван алгоритм 1.
"""
import re, sys, random, collections, statistics as st

# ── чтение и очистка ────────────────────────────────────────────────────────
def clean(t):
    t = re.sub(r"\[([^\]:.]+)[:.][^\]]*\]", r"\1", t)   # [y:o]->y, [ch:a]->ch
    t = re.sub(r"\{[^}]*\}", "", t)              # {ckhh} -> прочь
    t = re.sub(r"@(\d+);", lambda m: chr(0x3400 + int(m.group(1))), t)  # @192; -> свой знак
    return t.replace("?", "")

ZPAGES = ("f70", "f71", "f72", "f73")
rows, cur = [], None
for ln in open("ZL3b-n.txt", encoding="utf-8", errors="ignore"):
    m = re.match(r"<(f\d+[rv]\d*)>", ln)
    if m: cur = m.group(1); continue
    m = re.match(r"<(f\d+[rv]\d*)\.(\d+),([@&+*])(\w+)>\s*(?:<!(\d\d:\d\d)>)?(.*)", ln)
    if m:
        pg, num, mk, loc, ck, tx = m.groups()
        rows.append(dict(pg=pg, n=int(num), mk=mk, loc=loc, ck=ck, tx=clean(tx.strip())))

def label(t):  # подпись как единица: слова склеены
    return "".join(w for w in re.split(r"[.,]", t) if w)

# страницы зодиака -> список подписей в порядке обхода колец
PAGES = {}
for r in rows:
    if not r["pg"].startswith(ZPAGES) or r["loc"] != "Lz": continue
    PAGES.setdefault(r["pg"], []).append(label(r["tx"]))
PAGES = {p: [w for w in v if w] for p, v in PAGES.items()}
P30 = {p: v for p, v in PAGES.items() if len(v) == 30}

print("=" * 96); print("ДАННЫЕ"); print("=" * 96)
for p in sorted(PAGES): print(f"   {p:>7s}  {len(PAGES[p]):2d} подписей   {' '.join(PAGES[p][:6])} …")
print(f"\n   страниц ровно с 30 подписями: {len(P30)}  ({', '.join(sorted(P30))})")

# ── сходство ────────────────────────────────────────────────────────────────
def lcs(a, b):
    if not a or not b: return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        curr = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            curr[j] = prev[j-1] + 1 if x == y else max(prev[j], curr[j-1])
        prev = curr
    return prev[-1]
from functools import lru_cache
@lru_cache(maxsize=None)
def sim(a, b):
    if not a or not b: return 0.0
    if a > b: a, b = b, a
    return lcs(a, b) / max(len(a), len(b))

# ── S4: согласие по месту между страницами ──────────────────────────────────
def cross(seqs):
    """средняя по парам страниц доля совпадения при ЛУЧШЕМ повороте"""
    ps = list(seqs); tot = []
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            a, b, n = ps[i], ps[j], len(ps[i])
            tot.append(max(st.mean(sim(a[k], b[(k + off) % n]) for k in range(n))
                           for off in range(n)))
    return st.mean(tot)

print("\n" + "=" * 96)
print("S4 (ГЛАВНАЯ) — СОГЛАСИЕ ПОДПИСЕЙ ПО МЕСТУ МЕЖДУ СТРАНИЦАМИ, лучший поворот")
print("=" * 96)
obs4 = cross(P30.values())
rnd = random.Random(30)
null4 = []
for _ in range(1000):
    sh = {}
    for p, v in P30.items():
        c = v[:]; rnd.shuffle(c); sh[p] = c
    null4.append(cross(sh.values()))
p4 = sum(1 for x in null4 if x >= obs4) / len(null4)
print(f"   наблюдено           {obs4:.4f}")
print(f"   нуль (перемешивание внутри страницы, 1000 раз)  {st.mean(null4):.4f} "
      f"[{min(null4):.4f}; {max(null4):.4f}]")
print(f"   p = {p4:.4f}   ->  {'ЗНАЧИМО' if p4 < 0.01 else 'НЕ ЗНАЧИМО при пороге 0,01'}")

# ── наборы для сравнения ────────────────────────────────────────────────────
def chunks(ws, n=30):
    return [ws[i:i+n] for i in range(0, len(ws) - n + 1, n)]

TXT = [w for r in rows if r["pg"].startswith(ZPAGES) and r["loc"] in ("Cc", "P1", "Ri")
       for w in re.split(r"[.,]", r["tx"]) if w]
N2 = chunks(TXT)                                              # сплошной текст ТЕХ ЖЕ страниц
LF = [label(r["tx"]) for r in rows if r["loc"] == "Lf" and label(r["tx"])]
LS = [label(r["tx"]) for r in rows if r["loc"] == "Ls" and label(r["tx"])]
N3f, N3s = chunks(LF), chunks(LS)
GROUPS = [("зодиак, подписи", list(P30.values())),
          ("N2 сплошной текст тех же стр.", N2),
          ("N3 подписи травника (Lf)", N3f),
          ("N3 подписи звёзд (Ls)", N3s)]
print(f"\n   наборы: N2 {len(N2)} отрезков; N3 травник {len(N3f)}, звёзды {len(N3s)}")

# ── S1: профиль сходства по сдвигу ──────────────────────────────────────────
def profile(seqs, K=15):
    out = []
    for k in range(1, K + 1):
        v = [sim(s[i], s[i+k]) for s in seqs for i in range(len(s) - k)]
        out.append(st.mean(v) if v else 0.0)
    return out

print("\n" + "=" * 96)
print("S1 — ПРОФИЛЬ СХОДСТВА ПО СДВИГУ (счёт даёт ГОРБ на основании системы)")
print("=" * 96)
print(f"   {'набор':>30s} " + " ".join(f"{k:>5d}" for k in range(1, 16)))
prof = {}
for nm, g in GROUPS:
    prof[nm] = profile(g)
    print(f"   {nm:>30s} " + " ".join(f"{x:5.3f}" for x in prof[nm]))
print("\n   локальные максимумы при сдвиге 3..15 (горб = соседи слева и справа ниже):")
for nm, _ in GROUPS:
    q = prof[nm]
    bumps = [k for k in range(3, 15) if q[k-1] > q[k-2] and q[k-1] > q[k]]
    print(f"   {nm:>30s}  {bumps if bumps else 'нет'}")

zs = list(P30.values())
rnd2 = random.Random(1)
nullp = []
for _ in range(300):
    sh = []
    for v in zs:
        c = v[:]; rnd2.shuffle(c); sh.append(c)
    nullp.append(profile(sh))
print("\n   зодиак против перемешивания внутри страницы (300 раз), z по каждому сдвигу:")
zline = []
for k in range(15):
    col = [n[k] for n in nullp]
    sd = st.pstdev(col) or 1e-12
    zline.append((prof["зодиак, подписи"][k] - st.mean(col)) / sd)
print(f"   {'z':>30s} " + " ".join(f"{x:5.1f}" for x in zline))

# ── S2: блочность ───────────────────────────────────────────────────────────
def runs_ratio(seq):
    """число серий на знак, нормированное числом подписей со знаком; меньше = блочнее"""
    gl = collections.Counter(g for w in seq for g in set(w))
    tot = den = 0
    for g, c in gl.items():
        if c < 3 or c > len(seq) - 2: continue
        pres = [g in w for w in seq]
        tot += sum(1 for i, x in enumerate(pres) if x and (i == 0 or not pres[i-1]))
        den += c
    return tot / den if den else 0.0

print("\n" + "=" * 96)
print("S2 — БЛОЧНОСТЬ (серий на знак; ниже единицы = знак держится куском)")
print("=" * 96)
rnd3 = random.Random(2)
print(f"   {'набор':>30s} {'наблюдено':>10s} {'нуль':>8s} {'отношение':>10s} {'p':>7s}")
S2 = {}
for nm, g in GROUPS:
    obs = st.mean(runs_ratio(s) for s in g)
    nl = []
    for _ in range(300):
        acc = []
        for v in g:
            c = list(v); rnd3.shuffle(c); acc.append(runs_ratio(c))
        nl.append(st.mean(acc))
    pv = sum(1 for x in nl if x <= obs) / len(nl)
    S2[nm] = (obs, st.mean(nl), obs / st.mean(nl), pv)
    print(f"   {nm:>30s} {obs:10.4f} {st.mean(nl):8.4f} {obs/st.mean(nl):10.4f} {pv:7.3f}")

# ── S3: длина ───────────────────────────────────────────────────────────────
print("\n" + "=" * 96)
print("S3 — ДЛИНА ПОДПИСИ ПРОТИВ МЕСТА В КОЛЬЦЕ")
print("=" * 96)
xs = [i for s in zs for i in range(len(s))]
ys = [len(w) for s in zs for w in s]
mx, my = st.mean(xs), st.mean(ys)
r = (sum((a-mx)*(b-my) for a, b in zip(xs, ys)) /
     ((sum((a-mx)**2 for a in xs) * sum((b-my)**2 for b in ys)) ** .5))
print(f"   связь длины с местом: r = {r:+.4f}  (n = {len(xs)})")
bylen = [st.mean(len(s[i]) for s in zs) for i in range(30)]
print("   средняя длина по местам 1..30:")
print("   " + " ".join(f"{x:4.1f}" for x in bylen))

# ── итог по объявленному критерию ───────────────────────────────────────────
print("\n" + "=" * 96); print("ИТОГ ПО КРИТЕРИЮ, ОБЪЯВЛЕННОМУ ДО ЗАПУСКА"); print("=" * 96)
s2z = S2["зодиак, подписи"]
ok1 = any(zline[k-1] > 2.58 for k in range(3, 16))
ok2 = s2z[3] < 0.01 and all(s2z[2] < S2[n][2] for n, _ in GROUPS[1:])
print(f"   S4 согласие по месту между страницами : p = {p4:.4f}   "
      f"{'прошла' if p4 < 0.01 else 'НЕ ПРОШЛА'}")
print(f"   S1 горб в профиле сдвига (z > 2,58)   : {'прошла' if ok1 else 'НЕ ПРОШЛА'}")
print(f"   S2 блочность выше обоих нулей         : {'прошла' if ok2 else 'НЕ ПРОШЛА'}")
print(f"\n   СЧЁТ ПОКАЗАН: {'ДА' if (p4 < 0.01 or (ok1 and ok2)) else 'НЕТ'}")

# ── ПРОВЕРКА ЧУВСТВИТЕЛЬНОСТИ: увидела бы S4 счёт, если бы он был ───────────
# Отрицательный итог ничего не стоит, пока не показано, что прибор способен
# поймать явление. Строим ЗАВЕДОМО СЧЁТНЫЕ страницы из настоящего словаря
# подписей: 30 «числительных», у каждой страницы свой поворот начала отсчёта,
# доля мест испорчена посторонним словом. Смотрим, при какой порче S4 слепнет.
print("\n" + "=" * 96)
print("ПОЛОЖИТЕЛЬНЫЙ КОНТРОЛЬ: ЧТО ДАЛА БЫ S4, ЕСЛИ БЫ ПОДПИСИ ДЕЙСТВИТЕЛЬНО СЧИТАЛИ")
print("=" * 96)
POOL = [w for v in P30.values() for w in v]
rc = random.Random(7)
print(f"   {'испорчено мест':>16s} {'наблюдено':>10s} {'нуль':>8s} {'p':>8s}   вывод")
for frac in (0.0, 0.3, 0.6, 0.8, 0.9, 1.0):
    numerals = rc.sample(POOL, 30)
    fake = []
    for _ in range(7):
        off = rc.randrange(30)
        pg = [numerals[(i + off) % 30] for i in range(30)]
        for i in range(30):
            if rc.random() < frac: pg[i] = rc.choice(POOL)
        fake.append(pg)
    o = cross(fake)
    nl = []
    for _ in range(100):
        sh = []
        for v in fake:
            c = v[:]; rc.shuffle(c); sh.append(c)
        nl.append(cross(sh))
    pv = sum(1 for x in nl if x >= o) / len(nl)
    print(f"   {frac*100:>14.0f} % {o:10.4f} {st.mean(nl):8.4f} {pv:8.3f}   "
          f"{'ловит' if pv < 0.01 else 'слепа'}")
print(f"\n   для сравнения, настоящий зодиак: {obs4:.4f} при нуле {st.mean(null4):.4f}, p = {p4:.4f}")

# ── УСТОЙЧИВОСТЬ S4: выравнивание ПО УГЛУ, а не по обходу колец ─────────────
# Не пятая проверка, а та же S4 при иначе выведенном порядке. Оговорка, которую
# она снимает: выше подписи шли в порядке обхода колец из файла, а «градус» —
# величина УГЛОВАЯ. Здесь все 30 подписей страницы сливаются в один список по
# АБСОЛЮТНОМУ углу на циферблате, кольца игнорируются. Это другой порядок.
print("\n" + "=" * 96)
print("УСТОЙЧИВОСТЬ S4 — ВЫРАВНИВАНИЕ ПО УГЛУ НА ЦИФЕРБЛАТЕ (кольца слиты)")
print("=" * 96)
byang = {}
for r in rows:
    if not r["pg"].startswith(ZPAGES) or r["loc"] != "Lz" or not r["ck"]: continue
    w = label(r["tx"])
    if not w: continue
    h, mi = map(int, r["ck"].split(":"))
    byang.setdefault(r["pg"], []).append(((h % 12) * 30 + mi * 0.5, w))
A30 = {p: [w for _, w in sorted(v)] for p, v in byang.items() if len(v) == 30}
print(f"   страниц с 30 подписями при угловом порядке: {len(A30)} ({', '.join(sorted(A30))})")
obsA = cross(A30.values())
rnd4 = random.Random(99)
nullA = []
for _ in range(500):
    sh = []
    for v in A30.values():
        c = v[:]; rnd4.shuffle(c); sh.append(c)
    nullA.append(cross(sh))
pA = sum(1 for x in nullA if x >= obsA) / len(nullA)
print(f"   наблюдено {obsA:.4f}   нуль {st.mean(nullA):.4f} [{min(nullA):.4f}; {max(nullA):.4f}]"
      f"   p = {pA:.4f}   ->  {'ЗНАЧИМО' if pA < 0.01 else 'НЕ ЗНАЧИМО'}")
print(f"   для сравнения, порядок по обходу колец: {obs4:.4f} при нуле {st.mean(null4):.4f}, p = {p4:.4f}")
