# -*- coding: utf-8 -*-
"""MARKDOWN -> LaTeX для подачи на arXiv. Pandoc на машине нет, да и не нужен:
таблиц здесь 26 и все простые, а нумерация разделов РУЧНАЯ (есть §6a и §7a,
которых автонумерация LaTeX не даёт). Поэтому \\section* с номером в названии,
а ссылки §3.1 остаются буквальными — они не могут разъехаться.

Порядок обработки существенен: сперва выкусываются код и таблицы, потом
экранируются спецсимволы, и только потом ставится разметка — иначе обратные
косые от разметки экранируются сами.
"""
import re, sys

GREEK = {"ρ":r"\rho","σ":r"\sigma","μ":r"\mu","χ":r"\chi","≈":r"\approx","≤":r"\leq",
         "≥":r"\geq","×":r"\times","÷":r"\div","→":r"\to","·":r"\cdot","²":"^2"}
def esc(t):
    """экранировать спецсимволы LaTeX; математические знаки — в $...$"""
    t = t.replace("\\", r"\textbackslash{}")
    for c in "&%$#_{}": t = t.replace(c, "\\" + c)
    t = t.replace("~", r"\textasciitilde{}").replace("^", r"\textasciicircum{}")
    for k, v in GREEK.items(): t = t.replace(k, f"${v}$")
    t = t.replace("—", "---").replace("–", "--").replace("−", "$-$")
    t = t.replace("“", "``").replace("”", "''").replace("‘", "`").replace("’", "'")
    t = t.replace("§", r"\S").replace("±", r"$\pm$").replace("…", r"\ldots{}")
    t = re.sub(r"(?<!\.)\.\.\.(?!\.)", r"\\ldots{}", t)
    return t

def inline(t):
    """разметка внутри абзаца; вызывается ПОСЛЕ esc()"""
    t = re.sub(r"\bFigure (\d+)\b", r"Figure~\\ref{fig:\1}", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t)   # .+? — внутри бывает *курсив*
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\\emph{\1}", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: r"\href{%s}{%s}" % (m.group(2).replace("%","\\%"), m.group(1)), t)
    return t

def convert(md):
    src = md.split("\n")
    out, i, codes = [], 0, []
    def hold(line):                       # `код` вынуть до экранирования
        return re.sub(r"`([^`]+)`", lambda m: (codes.append(m.group(1)), f"\x00{len(codes)-1}\x00")[1], line)
    def give(line):
        return re.sub(r"\x00(\d+)\x00", lambda m: r"\texttt{%s}" % esc(codes[int(m.group(1))]).replace("\x00",""), line)
    def para(line):
        return give(inline(esc(hold(line))))

    while i < len(src):
        ln = src[i]
        # ── таблица ────────────────────────────────────────────────────────
        if ln.startswith("|") and i + 1 < len(src) and re.match(r"^\|[\s:|-]+\|?$", src[i+1]):
            head = [c.strip() for c in ln.strip("|").split("|")]
            i += 2; body = []
            while i < len(src) and src[i].startswith("|"):
                body.append([c.strip() for c in src[i].strip("|").split("|")]); i += 1
            ncol = len(head)
            out += [r"\begin{table}[htbp]\centering\small",
                    r"\begin{tabular}{@{}l" + "r" * (ncol - 1) + r"@{}}",
                    r"\toprule",
                    " & ".join(para(c) for c in head) + r" \\",
                    r"\midrule"]
            for row in body:
                row = (row + [""] * ncol)[:ncol]
                out.append(" & ".join(para(c) for c in row) + r" \\")
            out += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
            continue
        # ── фигура ─────────────────────────────────────────────────────────
        m = re.match(r"^!\[Figure (\d+)\]\(img/fig/fig(\d+)[^)]*\)", ln)
        if m:
            cap = ""
            if i + 2 < len(src) and src[i+2].startswith("*Figure"):
                j = i + 2; buf = []
                while j < len(src) and src[j].strip():
                    buf.append(src[j]); j += 1
                cap = " ".join(buf).strip().strip("*")
                cap = re.sub(r"^Figure \d+\.\s*", "", cap)
                i = j
            out += [r"\begin{figure}[htbp]\centering",
                    r"\input{fig/fig%s.tex}" % m.group(2),
                    (r"\caption{%s}" % para(cap)) if cap else "",
                    r"\label{fig:%s}" % m.group(2),
                    r"\end{figure}", ""]
            i += 1
            continue
        # ── заголовки ──────────────────────────────────────────────────────
        if ln.startswith("### "):
            out += [r"\subsection*{%s}" % para(ln[4:]), ""]; i += 1; continue
        if ln.startswith("## "):
            t = ln[3:]
            out += [r"\section*{%s}" % para(t), ""]; i += 1; continue
        if ln.startswith("# "):
            i += 1; continue                       # заголовок статьи ставит преамбула
        # ── списки ─────────────────────────────────────────────────────────
        if re.match(r"^[-*] ", ln) or re.match(r"^\d+\. ", ln):
            env = "itemize" if re.match(r"^[-*] ", ln) else "enumerate"
            out.append(r"\begin{%s}\setlength\itemsep{0pt}" % env)
            item = []
            def flush():
                if item: out.append(r"\item " + para(" ".join(item))); item.clear()
            while i < len(src) and (re.match(r"^[-*] ", src[i]) or re.match(r"^\d+\. ", src[i]) or
                                    (src[i].startswith("  ") and src[i].strip())):
                if re.match(r"^[-*] |^\d+\. ", src[i]):
                    flush(); item.append(re.sub(r"^([-*]|\d+\.) ", "", src[i]))
                else:
                    item.append(src[i].strip())      # продолжение пункта: жирный может идти ЧЕРЕЗ перенос
                i += 1
            flush()
            out += [r"\end{%s}" % env, ""]; continue
        # ── обычный абзац ──────────────────────────────────────────────────
        if not ln.strip():
            out.append(""); i += 1; continue
        buf = []
        while i < len(src) and src[i].strip() and not src[i].startswith(("#", "|", "!", "- ")) \
                and not re.match(r"^\d+\. ", src[i]):
            buf.append(src[i]); i += 1
        out += [para(" ".join(buf)), ""]
    return "\n".join(out)

if __name__ == "__main__":
    sys.stdout.write(convert(open(sys.argv[1], encoding="utf-8").read()))
