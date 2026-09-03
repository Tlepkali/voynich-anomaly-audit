# -*- coding: utf-8 -*-
"""ОСТАТОК СТРОКИ: второй механизм или разная чувствительность мер.

ВОПРОС. Одно правило (приписать знак спереди с вероятностью p) поднимает все три
явления начала строки, но НЕ В ТЕХ ПРОПОРЦИЯХ: расхождению нужно p ≈ 0,85,
доле Гроува ≈ 0,75, словам только-в-началах ≈ 0,3.

ДВЕ ГИПОТЕЗЫ, ОБЪЯВЛЕНЫ ДО ЗАПУСКА.

  H1 — РАЗНАЯ ЧУВСТВИТЕЛЬНОСТЬ. Меры расходятся не из-за второго механизма,
  а потому что две из трёх считают не то, что называют:
    * «слова только-в-началах» — СЫРОЙ СЧЁТ ТИПОВ. Приписывание создаёт НОВЫЕ
      типы (знак + слово), каждый редкий, а редкий тип почти наверняка попадёт
      «только в начало». Мера растёт от побочного следствия, а не от явления.
    * «доля Гроува» проверяет разложимость по СОБСТВЕННОМУ словарю текста.
      Приписывание разом поднимает и числитель, и словарь — та же круговая
      зависимость от плотности, из-за которой отозван алгоритм 1 (§3 аудита).
  ПРЕДСКАЗАНИЕ H1: если считать долю, а не счёт, и разлагать по ФИКСИРОВАННОМУ
  словарю рукописи, оптимальные p сойдутся (разброс ≤ 0,15).

  H2 — ВТОРОЙ МЕХАНИЗМ. Расхождение переживёт исправление мер.
  ПРЕДСКАЗАНИЕ H2: разброс оптимальных p останется > 0,15, и останется
  структурный остаток, который приписывание не воспроизводит.

Решение принимается по разбросу оптимальных p ПОСЛЕ исправления мер.
Порог 0,15 назначен здесь, до первого запуска.
"""
import json, collections, random, statistics as st, math, sys
exec(open("scripts/arch_line.py").read().split('V=dict(ldiv=')[0])

VT_MS = set(VOY)                      # словарь РУКОПИСИ — фиксированная опора

# ── меры в двух видах: как были и исправленные ──────────────────────────────

def grove_own(L):
    """как было: разложение по СОБСТВЕННОМУ словарю текста (зависит от плотности)"""
    T = set(w for l in L for w in l); n = d = 0
    for l in L:
        w = l[0]; n += 1
        if len(w) > 2 and w[1:] in T: d += 1
    return d / max(n, 1)

def grove_fixed(L):
    """исправленная: разложение по словарю РУКОПИСИ, один и тот же для всех моделей"""
    n = d = 0
    for l in L:
        w = l[0]; n += 1
        if len(w) > 2 and w[1:] in VT_MS: d += 1
    return d / max(n, 1)

def only_count(L):
    """как было: СЫРОЙ СЧЁТ типов, встречающихся только в начале строки"""
    fi = collections.Counter(l[0] for l in L if l)
    mid = collections.Counter(w for l in L for w in l[1:])
    return sum(1 for w in fi if w not in mid)

def only_rate(L):
    """исправленная: ДОЛЯ таких типов среди всех начальных типов"""
    fi = collections.Counter(l[0] for l in L if l)
    mid = collections.Counter(w for l in L for w in l[1:])
    return sum(1 for w in fi if w not in mid) / max(len(fi), 1)

def only_rate_freq(L, minf=2):
    """исправленная жёстче: только типы, встреченные в тексте не реже minf раз —
    гапаксы попадают «только в начало» по чистой редкости"""
    cnt = collections.Counter(w for l in L for w in l)
    fi = {l[0] for l in L if l and cnt[l[0]] >= minf}
    mid = {w for l in L for w in l[1:]}
    return sum(1 for w in fi if w not in mid) / max(len(fi), 1)

MEAS = [("расхождение", line_div, "ldiv"),
        ("Гроув, свой словарь", grove_own, "g_own"),
        ("Гроув, словарь рукописи", grove_fixed, "g_fix"),
        ("только-в-нач., счёт", only_count, "o_cnt"),
        ("только-в-нач., доля", only_rate, "o_rate"),
        ("только-в-нач., доля f≥2", only_rate_freq, "o_freq")]

TARGET = {k: fn(VL) for _, fn, k in MEAS}
print("=" * 104); print("РУКОПИСЬ"); print("=" * 104)
for nm, _, k in MEAS:
    v = TARGET[k]
    print(f"  {nm:>26s} {v:10.4f}" + ("" if k != "o_cnt" else "   (счёт типов)"))

# контроль: что дают меры, когда строчной структуры НЕТ вовсе
print("\n  контроль — те же слова, перемешанные внутри страницы (строчной структуры нет):")
rnd = random.Random(11)
flat = [w for l in VL for w in l]; sh = flat[:]; rnd.shuffle(sh)
SHUF = []; i = 0
for l in VL: SHUF.append(sh[i:i + len(l)]); i += len(l)
for nm, fn, k in MEAS:
    print(f"  {nm:>26s} {fn(SHUF):10.4f}")

# ── развёртка по p ──────────────────────────────────────────────────────────
GRID = [round(0.05 * i, 2) for i in range(0, 21)]
SEEDS = range(3)
print("\n" + "=" * 104); print(f"РАЗВЁРТКА ПО p ({len(GRID)} точек x {len(SEEDS)} зерна)"); print("=" * 104)
print(f"  {'p':>5s} " + " ".join(f"{k:>10s}" for _, _, k in MEAS))
rows = {}
for p in GRID:
    Ls = [gen_lines(p, seed=s) for s in SEEDS]
    rows[p] = {k: st.mean(fn(L) for L in Ls) for _, fn, k in MEAS}
    print(f"  {p:5.2f} " + " ".join(f"{rows[p][k]:10.4f}" for _, _, k in MEAS))
    sys.stdout.flush()

print("\n" + "=" * 104); print("ОПТИМАЛЬНОЕ p ПО КАЖДОЙ МЕРЕ"); print("=" * 104)
best = {}
for nm, _, k in MEAS:
    t = TARGET[k]
    b = min(GRID, key=lambda p: abs(rows[p][k] - t))
    best[k] = b
    print(f"  {nm:>26s}  p* = {b:4.2f}   при нём {rows[b][k]:9.4f} против цели {t:9.4f}")

OLD = [best["ldiv"], best["g_own"], best["o_cnt"]]
NEW = [best["ldiv"], best["g_fix"], best["o_rate"]]
NEW2 = [best["ldiv"], best["g_fix"], best["o_freq"]]
print(f"\n  разброс p* КАК БЫЛО              : {max(OLD) - min(OLD):.2f}   ({OLD})")
print(f"  разброс p* ПОСЛЕ ИСПРАВЛЕНИЯ МЕР : {max(NEW) - min(NEW):.2f}   ({NEW})")
print(f"  то же с порогом частоты f>=2     : {max(NEW2) - min(NEW2):.2f}   ({NEW2})")
verdict = "H1 — РАЗНАЯ ЧУВСТВИТЕЛЬНОСТЬ" if max(NEW) - min(NEW) <= 0.15 else "H2 — ОСТАТОК ЕСТЬ"
print(f"\n  порог 0,15 объявлен до запуска. ВЕРДИКТ: {verdict}")
