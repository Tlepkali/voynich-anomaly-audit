# Voynich anomaly audit

Code and working materials for an audit of claimed statistical peculiarities of
the Voynich manuscript. Fifty-eight claims — other people's and our own — each
re-tested against a null model matched to the unit the claim concerns. Eighteen
survive as stated; seven of the retractions are of claims we made ourselves.

The draft write-up is `paper-draft.md`. It is not submitted anywhere and we would
rather be corrected than not.

## What is here

    scripts/            ~186 files, standard library only (one exception below)
    scripts/inventory.py    the audit itself: 58 machine-readable records with
                            claim / source / control applied / numbers / outcome
    scripts/fetch_data.sh   downloads the data, which is not in this repository
    paper-draft.md      draft, ~7,600 words
    report.html         the full working record, in Russian, 71 sections
    img/                IIIF crops from Beinecke MS 408 (public domain)

## The data is not here, deliberately

Transliterations, reference corpora and forum archives are other people's
material and not ours to redistribute. `scripts/fetch_data.sh` downloads what it
can:

    sh scripts/fetch_data.sh

It retrieves the six IVTFF transliterations from voynich.nu, parses them, and
fetches book-length corpora from Project Gutenberg. What it cannot restore
automatically is listed at the end of its output.

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
28.8% of its 7,205 word types**, against 1.5–5.8% for language corpora matched on
both vocabulary size and word length.

**Four kinds of memory are needed in generation, and they compete for one
decision.** A generator that selects whole words reproduces three of the four
sequence signatures but not the information across the word boundary, at any
parameter setting we could find. That last one appears to be a property of how a
word is built rather than of which word is chosen.

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

Code under MIT (see LICENSE). The prose in `paper-draft.md`, `report.html` and the
forum posts is CC BY 4.0.
