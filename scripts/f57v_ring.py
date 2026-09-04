# -*- coding: utf-8 -*-
"""КОЛЬЦО f57v ПРОТИВ ПОРЯДКА ЗНАКОВ, ВЫВЕДЕННОГО ИЗ ТЕКСТА.

ЗАЧЕМ. Разбор Цифрального дистиха (Уркварт 1653, решён 2026) держался на том,
что КЛЮЧ ЛЕЖАЛ В САМОЙ КНИГЕ: предыдущие решатели искали внешний ключ, а
работал внутренний — 32 раздела того же тома. Ближайший предмет такого рода в
рукописи Войнича — строка f57v.3: 17 знаков, выписанных ЧЕТЫРЕЖДЫ подряд почти
без разночтений. Четырёхкратный повтор сам по себе говорит, что это НЕ текст, а
намеренный перечень — то есть возможный внутренний ключ.

ЧТО ПРОВЕРЯЕМ. Из аудита (запись «жёсткость слотов», 6,98x против перестановки
букв внутри слова) известно: знаки занимают в слове устойчивые места слева
направо. Значит ТЕКСТ САМ ЗАДАЁТ порядок знаков — по среднему месту в слове.
Вопрос: совпадает ли порядок кольца с этим выведенным порядком?

ДВЕ ГИПОТЕЗЫ, ОБЪЯВЛЕНЫ ДО ЗАПУСКА.
  HA — кольцо упорядочено по МЕСТУ В СЛОВЕ (ранняя позиция -> начало кольца).
  HB — кольцо упорядочено по ЧАСТОТЕ знака в тексте.

НУЛЬ у обеих один: перестановка порядка кольца (10 000 раз). Мера — ро Спирмена
по знакам, попавшим в оба списка; позиции исключённых знаков в кольце
СОХРАНЯЮТСЯ, чтобы не поплыла нумерация.

КРИТЕРИЙ, НАЗНАЧЕН ЗДЕСЬ И ДО ПЕРВОГО ЗАПУСКА. Две гипотезы -> порог 0,01 на
каждую (0,02 суммарно). Отрицательный итог по обеим есть ОТРИЦАТЕЛЬНЫЙ ИТОГ:
он закрывает «кольцо f57v = алфавитный порядок» в двух самых естественных
прочтениях и НЕ даёт права перебирать третье, четвёртое и так далее.
"""
import sys, re, json, collections, random, statistics as st
sys.path.insert(0, "scripts")
import measures as M

# ── кольцо ──────────────────────────────────────────────────────────────────
raw = [l for l in open("ZL3b-n.txt", encoding="utf-8", errors="ignore")
       if l.startswith("<f57v.3,")][0].split(">", 1)[1]
raw = raw.split("!10:30>")[-1].strip()
syms = [s for s in re.split(r"[.,]", raw) if s]
def norm(s):
    s = re.sub(r"\[(.)[:.].*?\]", r"\1", s)      # [d:j] -> d
    return s.strip()
syms = [norm(s) for s in syms]

# четыре повтора: режем по вхождениям начала "o","l"
starts = [i for i in range(len(syms) - 1) if syms[i] == "o" and syms[i+1] == "l"]
reps = [syms[a:b] for a, b in zip(starts, starts[1:] + [len(syms)])]
print("=" * 78); print("КОЛЬЦО f57v.3"); print("=" * 78)
for i, r in enumerate(reps, 1):
    print(f"  повтор {i} ({len(r):2d} знаков): {' '.join(r)}")

n = min(len(r) for r in reps)
consensus = [collections.Counter(r[i] for r in reps).most_common(1)[0][0] for i in range(n)]
print(f"\n  согласие по {len(reps)} повторам, длина {n}:")
print(f"    {' '.join(consensus)}")
disagree = [i for i in range(n) if len({r[i] for r in reps}) > 1]
print(f"    разночтений: {len(disagree)} из {n} (места {disagree})")

# ── выведенный из текста порядок ────────────────────────────────────────────
VL = M.load(); tv = M.tokens(VL)
pos, freq = collections.defaultdict(list), collections.Counter()
for w in tv:
    for i, g in enumerate(w):
        freq[g] += 1
        if len(w) > 1: pos[g].append(i / (len(w) - 1))
MEANPOS = {g: st.mean(v) for g, v in pos.items() if len(v) >= 100}

usable = [(i, g) for i, g in enumerate(consensus) if g in MEANPOS]
print("\n" + "=" * 78); print("ЗНАКИ, ПОПАВШИЕ В ОБА СПИСКА"); print("=" * 78)
print(f"  {'место в кольце':>15s} {'знак':>5s} {'ср. место в слове':>18s} {'частота':>9s}")
for i, g in usable:
    print(f"  {i+1:>15d} {g:>5s} {MEANPOS[g]:>18.3f} {freq[g]:>9,d}")
print(f"\n  использовано {len(usable)} из {n} знаков кольца"
      f"  (отброшены: {[g for i,g in enumerate(consensus) if g not in MEANPOS]})")

def spearman(a, b):
    def rk(x):
        s = sorted(range(len(x)), key=lambda i: x[i]); r = [0]*len(x)
        for j, i in enumerate(s): r[i] = j
        return r
    ra, rb = rk(a), rk(b); m = len(a)
    ma, mb = st.mean(ra), st.mean(rb)
    num = sum((ra[i]-ma)*(rb[i]-mb) for i in range(m))
    den = (sum((r-ma)**2 for r in ra) * sum((r-mb)**2 for r in rb)) ** .5
    return num/den if den else 0.0

ringpos = [i for i, g in usable]
print("\n" + "=" * 78); print("ПРОВЕРКА, 10 000 ПЕРЕСТАНОВОК КОЛЬЦА"); print("=" * 78)
rnd = random.Random(57)
for name, vals in [("HA  место в слове", [MEANPOS[g] for _, g in usable]),
                   ("HB  частота знака", [freq[g] for _, g in usable])]:
    obs = spearman(ringpos, vals)
    null = []
    for _ in range(10000):
        p = ringpos[:]; rnd.shuffle(p); null.append(spearman(p, vals))
    p2 = sum(1 for x in null if abs(x) >= abs(obs)) / len(null)
    print(f"  {name:>22s}:  ро = {obs:+.3f}   нуль {st.mean(null):+.3f} "
          f"[{min(null):+.2f}; {max(null):+.2f}]   p = {p2:.4f}   "
          f"{'ЗНАЧИМО' if p2 < 0.01 else 'не значимо при пороге 0,01'}")
