# -*- coding: utf-8 -*-
"""ПЕРЕСЧЁТ НЕСУЩИХ ЧИСЕЛ ОБЕИХ СТАТЕЙ из scripts/measures.py.

Пишет data/paper_numbers.json: ключ -> {value, fmt, paper, context}.
Сверку с текстом статей делает scripts/check_paper.py (быстрая, читает json).

Запуск:  python3 scripts/paper_numbers.py            (без Morfessor)
         .venv/bin/python scripts/paper_numbers.py   (с Morfessor)

Заведено после сверки 03.09.2026: одиннадцать расхождений нашлись только
чтением подряд, и восемь из них поймал бы автомат.
"""
import sys, os, json, collections, statistics as st
sys.path.insert(0, "scripts")
import measures as M

OUT = []
def rec(key, value, fmt, paper, context=None, note=None):
    OUT.append(dict(key=key, value=value, fmt=fmt, paper=paper, context=context, note=note))
    return value

A, B = "paper-audit.md", "paper-generator.md"

print("загрузка…", file=sys.stderr)
VL = M.load(); LENS = [len(l) for l in VL]
LL = M.ref_lines("latin.clean", LENS)
TV, TL = M.types(VL), M.types(LL)
tv, tl = M.tokens(VL), M.tokens(LL)

# ── §2 данные ───────────────────────────────────────────────────────────────
rec("tokens_zl", len(tv), "{:,}", A, "Zandbergen–Landini")
rec("types_zl", len(TV), "{:,}", A, "word types")

# ── §4 типы против токенов ──────────────────────────────────────────────────
print("§4 типы/токены…", file=sys.stderr)
rec("mi_types_voy", M.mi_at(TV), "{:.3f}", A, "glyph–position MI, types")
rec("mi_types_lat", M.mi_at(TL), "{:.3f}", A, "glyph–position MI, types")
rec("mi_tokens_voy", M.mi_at(tv), "{:.3f}", A, "glyph–position MI, tokens")
rec("mi_tokens_lat", M.mi_at(tl), "{:.3f}", A, "glyph–position MI, tokens")
rec("rig_types_voy", M.slot_rigidity(TV), "{:.1f}", A, "excess over within-word shuffle, types")
rec("rig_types_lat", M.slot_rigidity(TL), "{:.1f}", A, "excess over within-word shuffle, types")
rec("rig_tokens_voy", M.slot_rigidity(tv), "{:.0f}", A, "excess over within-word shuffle, tokens")
rec("rig_tokens_lat", M.slot_rigidity(tl), "{:.0f}", A, "excess over within-word shuffle, tokens")
rec("h2_types_voy", M.h2_at(TV), "{:.2f}", A, "conditional entropy h2, types")
rec("h2_types_lat", M.h2_at(TL), "{:.2f}", A, "conditional entropy h2, types")
rec("h2_tokens_voy", M.h2_at(tv), "{:.2f}", A, "conditional entropy h2, tokens")
rec("h2_tokens_lat", M.h2_at(tl), "{:.2f}", A, "conditional entropy h2, tokens")

# h2 по алфавитам (транскрипционный эффект)
for code, key in [("ZL3b-n", "eva"), ("FG2a-n", "fsg"), ("GC2a-n", "v101")]:
    rec(f"h2_stream_{key}", M.h2_stream(M.load(code)), "{:.2f}", A, "character-level h2 of the running text")

# ── §3 разложения (базовые величины) ────────────────────────────────────────
print("§3 базовые…", file=sys.stderr)
rec("shape_voy", M.shape(TV), "{:.2f}", A, "neighbourhood-density ratio")
rec("shape_lat", M.shape(TL), "{:.2f}", A, "language range of")
rec("junc1_voy", M.junction(VL, 1), "{:.3f}", A, "mutual information across the word boundary")
rec("junc1_lat", M.junction(LL, 1), "{:.3f}", B, "moves only from")

# h2 по длинам слова (§4): в тексте стоят ОТНОШЕНИЯ, их и сверяем
for n_ in (3, 4, 5, 6, 7):
    rec(f"h2ratio_tok_len{n_}", M.h2_at(tv, n_) / M.h2_at(tl, n_), "{:.2f}", A, "gap is closer to unity at every length")
    rec(f"h2ratio_typ_len{n_}", M.h2_at(TV, n_) / M.h2_at(TL, n_), "{:.2f}", A, "gap is closer to unity at every length")

# §3.1 доли вывода по алгоритму 1, корпуса выравнены по объёму
print("§3.1 разложение по корпусам…", file=sys.stderr)
d_voy, t_voy, root_voy = M.affix_decompose(tv)
rec("alg1_der_voy", d_voy * 100, "{:.1f}", A, "derived for Voynichese against")
rec("alg1_twice_voy", t_voy * 100, "{:.1f}", A, "reducing twice or more")
for fn, lab in [("latin.clean", "lat"), ("scr_vulgata.clean", "vul"), ("bk_es.clean", "spa"),
                ("english.clean", "eng"), ("bk_it.clean", "ita"), ("bk_fr1.clean", "fra")]:
    d_, _, _ = M.affix_decompose(M.ref(fn, len(tv)))
    rec(f"alg1_der_{lab}", d_ * 100, "{:.1f}", A, "derived for Voynichese against")
d_cap, _, _ = M.affix_decompose(tv, cap=5000)
rec("alg1_der_voy_cap", d_cap * 100, "{:.1f}", A, "5,000 most frequent types")
C = M.strip_text(VL, root_voy)
rec("alg1_shape_after", M.shape(M.types(C)), "{:.2f}", A, "5 over length 3) fell from")
rec("alg1_junc_after", M.junction(C, 1), "{:.3f}", A, "excess single-character mutual information")
rec("alg1_rig_after", M.slot_rigidity(M.types(C)), "{:.2f}", A, "type-level glyph–position association fell")

# ── §5.1 плотность и перерождение ───────────────────────────────────────────
print("§5.1 плотность…", file=sys.stderr)
rec("dens_voy", M.density(TV), "{:.2f}", A, "edit-distance-1 neighbours")
rec("meanlen_types_voy", st.mean(len(w) for w in TV), "{:.2f}", A, "| **Voynich** | 7,205 |")
rec("dens_lat", M.density(TL), "{:.2f}", A, "against Latin's")
print("§5.1 перерождение (20 зёрен)…", file=sys.stderr)
rec("regen_voy_head", st.mean(M.regeneration(TV, 2, c) for c in range(3)) * 100, "{:.1f}", A,
    "| **Voynich** | 7,205 |")
rec("regen_voy_abstract", st.mean(M.regeneration(TV, 2, c) for c in range(3)) * 100, "{:.1f}", A,
    "of its 7,205 word types")
mean20, lo20, hi20 = M.regeneration_mean(TV, 2, range(20))
rec("regen_voy_mean20", mean20 * 100, "{:.1f}", A, "averaged over twenty seeds")
rec("regen_voy_lo", lo20 * 100, "{:.1f}", A, "range")
rec("regen_voy_hi", hi20 * 100, "{:.1f}", A, "range")
mV = st.mean(len(w) for w in TV)
for fn, lab in [("latin.clean", "lat"), ("bk_es.clean", "spa"), ("bk_it.clean", "ita")]:
    T = sorted(set(M.ref(fn)))
    print(f"  выравнивание {lab}…", file=sys.stderr)
    a = st.mean(M.regeneration(M.match_mean_length(T, len(TV), mV, seed=s), 2, c)
                for s in range(5) for c in range(3))
    b = st.mean(M.regeneration(M.match_length_dist(T, [len(w) for w in TV], len(TV), seed=s), 2, c)
                for s in range(5) for c in range(3))
    rec(f"regen_{lab}_meanlen", a * 100, "{:.1f}", A, "matched on mean length")
    rec(f"regen_{lab}_lendist", b * 100, "{:.1f}", A, "matched on the length distribution")

# ── §5.2 что осталось ───────────────────────────────────────────────────────
print("§5.2 стык по 3 знакам…", file=sys.stderr)
rec("junc3_voy", M.junction(VL, 3), "{:.3f}", A, "three-character information across the word boundary")
for fn, lab in [("latin.clean", "lat"), ("bk_it.clean", "ita"), ("bk_es.clean", "spa"),
                ("scr_vulgata.clean", "vul"), ("english.clean", "eng"), ("bk_fr1.clean", "fra")]:
    rec(f"junc3_{lab}", M.junction(M.ref_lines(fn, LENS), 3), "{:.3f}", A, "three-character")

# ── §6 ранг-корреляция ──────────────────────────────────────────────────────
print("§6 ранг-корреляция…", file=sys.stderr)
rec("rank_voy", M.rank_corr(VL), "{:+.4f}", A, "In the manuscript it is")
rec("rank_lat", M.rank_corr(LL), "{:+.3f}", A, "rank correlation")

# ── подписи последовательности (обе статьи) ─────────────────────────────────
print("подписи последовательности…", file=sys.stderr)
rec("recur_d15", M.recurrence(VL, 1, 5), "{:.2f}", B, "manuscript")
rec("recur_d620", M.recurrence(VL, 6, 20), "{:.2f}", B, "manuscript")
rec("recur_decay", M.recurrence_decay(VL), "{:d}", B, "d ≈")
rec("lenauto_voy", M.len_autocorr(VL), "{:+.3f}", B, "manuscript")

# ── §3 генеративной: доступность соседа ─────────────────────────────────────
print("доступность соседа…", file=sys.stderr)
rec("nbfrac_voy", M.has_neighbour(TV) * 100, "{:.1f}", B, "of its types have a neighbour")
for fn, lab in [("bk_it.clean", "ita"), ("bk_es.clean", "spa"), ("latin.clean", "lat")]:
    T = M.types(M.ref_lines(fn, LENS))
    rec(f"nbfrac_{lab}", M.has_neighbour(T) * 100, "{:.1f}", B, "cut to the manuscript's")
    rec(f"dens_{lab}", M.density(T), "{:.2f}", B, "cut to the manuscript's")

os.makedirs("data", exist_ok=True)
json.dump(OUT, open("data/paper_numbers.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nпосчитано {len(OUT)} величин -> data/paper_numbers.json")
for r in OUT:
    print(f"  {r['key']:>22s} {r['fmt'].format(r['value']):>10s}  {r['paper']}")
