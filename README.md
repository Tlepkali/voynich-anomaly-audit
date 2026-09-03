# Voynich anomaly audit

Code and working materials for an audit of claimed statistical peculiarities of
the Voynich manuscript. Seventy-four claims — other people's and our own — each
re-tested against a null model matched to the unit the claim concerns. 22
survive as stated; 11 are retractions, 10 of them of claims we made ourselves.

Two draft write-ups: `paper-audit.md` (what survives the controls) and
`paper-generator.md` (what the residue constrains about generative mechanisms).
Neither is submitted anywhere and we would rather be corrected than not.

## What is here

    scripts/            ~218 files, standard library only (one exception below)
    scripts/measures.py     one definition per quantity, seeds in the signatures
    scripts/inventory.py    the audit itself: 74 machine-readable records with
                            claim / source / control applied / numbers / outcome
    scripts/fetch_data.sh   downloads the data, which is not in this repository
    paper-audit.md      draft: the audit, ~7,300 words
    paper-generator.md  draft: generative constraints, ~4,800 words
    report.html         the full working record, in Russian, 74 sections
    Makefile            `make check` verifies the papers against the code
    img/                IIIF crops from Beinecke MS 408 (public domain)

## The data is not here, deliberately

Transliterations, reference corpora and forum archives are other people's
material and not ours to redistribute. `scripts/fetch_data.sh` downloads what it
can:

    sh scripts/fetch_data.sh

It retrieves the six IVTFF transliterations from voynich.nu, parses them, and
fetches book-length corpora from Project Gutenberg. What it cannot restore
automatically is listed at the end of its output.

## Checking the papers against the code

Each recurring quantity is defined once in `scripts/measures.py`, with its seed
and repetition count in the function signature. `make numbers` recomputes 77
load-bearing figures from those definitions; `make check` verifies that each
appears in the papers where it should, that the appendix matches the
machine-readable inventory row for row and verdict for verdict, and that no
section cross-reference dangles. It exits non-zero on any disagreement and
reports its own coverage — currently 13% of the numbers in the audit paper and
7% in the generative one, the rest being derived quantities and other people's
figures.

This is a check on arithmetic and bookkeeping, not on judgement. It found two
real defects on its first run and misses, by construction, the kind of error
that matters most: a defensible alternative procedure giving a different answer.

## Dependencies

Standard library only, except `scripts/decomp_morf.py`, which uses Morfessor
2.0.6 as an independent check on our own decomposition algorithms:

    python3 -m venv .venv && .venv/bin/pip install morfessor

Note that `scripts/struct.py` shadows the standard `struct` module when scripts
are run from that directory; `decomp_morf.py` clears it from `sys.path` before
importing third-party packages.

## Main results, briefly

**Most of the inventory does not survive its own controls.** The size of an
anomaly is usually decided by the choice of null model rather than by the data:
the same 274 adjacent repeats give 2.45×, 1.18× or 1.01× depending only on where
the shuffle boundary is drawn.

**Type and token are different questions.** Measuring a vocabulary property on a
token stream roughly doubles the manuscript's apparent distance from Latin on
both conditional entropy and glyph-position rigidity.

**A character bigram chain trained on the manuscript's own vocabulary regenerates
28.8% of its 7,205 word types**, against 3.5–6.6% for language corpora matched on
vocabulary size and on the whole distribution of word lengths. Matching the mean
length alone gives 1.7–5.9% and doubles the apparent gap; both are reported.

**The line start takes two operations, not one.** Prepending a character accounts
for the length of line-initial words but, at that rate, for less than half their
first-character divergence; an operation that changes the opening character
without changing the length closes the gap. A claim we made and withdrew the same
day is written up alongside it: its null model destroyed the mechanism whose
sufficiency was in question.

**Four kinds of memory are needed in generation, and they compete for one
decision.** A generator that selects whole words reproduces three of the four
sequence signatures but not the information across the word boundary, at any of
503 parameter settings. That last one is a property of how a word is built rather
than of which word is chosen: an architecture in which memory is weighted by the
boundary transition frequency reaches all four, to about four fifths of target
each and no better.

Everything is computed on six transliterations parsed with identical rules, two
of them in non-EVA alphabets, against eighteen reference corpora each at least as
large as the manuscript, and under two alternative word segmentations.

## Credit

This work depends on transliterations by Zandbergen and Landini, Takahashi,
Claston and the Friedman group, and on observations by Currier, Tiltman, Neal,
Stolfi, Timm, Jackson, Pelling, Emma May Smith, Zattera, Greshko, Parisel and the
voynich.ninja community. Where a result is a control under someone else's
observation, `scripts/inventory.py` says whose it is.

## Provenance

The measurements, the code and the choice of controls are the author's. The
English prose in the write-ups is machine-written.

## Licence

Code under MIT (see LICENSE). The prose in `paper-audit.md`, `paper-generator.md`
and `report.html` is CC BY 4.0.
