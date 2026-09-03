# Прогон проекта. Данные скачиваются отдельно: sh scripts/fetch_data.sh
PY   ?= python3
VENV ?= .venv/bin/python      # нужен только для Morfessor

.PHONY: check numbers verify-all inventory figures clean-numbers

check: data/paper_numbers.json          ## быстрая сверка статей с пересчитанным
	$(PY) scripts/check_paper.py

numbers data/paper_numbers.json:        ## пересчитать несущие числа (около 2 минут)
	$(PY) scripts/paper_numbers.py

verify-all: numbers check figures       ## пересчитать, сверить и перерисовать
	$(VENV) scripts/decomp_morf.py | tail -12
	$(VENV) scripts/one_instrument.py | tail -12

figures:                                ## пересобрать SVG-фигуры из манифеста
	$(PY) scripts/figures.py

inventory:                              ## пересобрать блок инвентаря для report.html
	$(PY) scripts/inv_render.py

clean-numbers:
	rm -f data/paper_numbers.json
