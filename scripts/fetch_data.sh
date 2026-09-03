#!/bin/sh
# Восстановление данных, которых нет в репозитории. Запускать из корня проекта.
set -e
mkdir -p data ref

echo "== транскрипции IVTFF с voynich.nu =="
for n in ZL3b-n IT2a-n RF1b-e GC2a-n FG2a-n CD2a-n; do
  [ -f "data/$n.txt" ] || curl -sL -o "data/$n.txt" "https://www.voynich.nu/data/$n.txt"
  printf "  %-10s %8d байт\n" "$n" "$(wc -c < data/$n.txt)"
done

echo "== разбор =="
ln -sf data/ZL3b-n.txt ZL3b-n.txt
ln -sf data/parsed.json parsed.json
python3 scripts/parse.py
python3 scripts/parse_any.py ZL3b-n IT2a-n RF1b-e GC2a-n FG2a-n CD2a-n

echo "== книжные корпуса с Project Gutenberg =="
python3 scripts/books.py

echo "== корпуса Википедии (долго; правит ref/wiki_*.clean) =="
echo "   python3 scripts/wiki_one.py <язык> <слов>   — по одному, с записью по ходу"
echo "   python3 scripts/wiki_big.py                 — пачкой"
echo
echo "Не восстанавливаются автоматически: forum/ (посты voynich.ninja),"
echo "naibbe/ (git clone https://github.com/greshko/naibbe-cipher),"
echo "ref/latin.clean и ref/scr_*.clean (Плиний и писание — см. scripts/mkref.py)."
