VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: run deps build-css test clean

run: deps build-css
	$(PYTHON) app.py

deps:
	@if [ ! -d $(VENV) ]; then \
		python3 -m venv $(VENV); \
	fi
	$(PIP) install --upgrade pip -q
	$(PIP) install -r requirements.txt -q
	@if [ -f package.json ]; then \
		npm install --silent; \
	fi
	@echo "의존성 설치 완료"

build-css:
	@if [ -f package.json ]; then \
		npm run build:css --silent; \
	fi

test: deps build-css
	$(PYTHON) -m pytest -q

clean:
	rm -rf $(VENV) node_modules
