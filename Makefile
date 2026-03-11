VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: run clean

## 가상환경 생성(없을 때만) → 의존성 설치 → 서버 실행
run:
	@if [ ! -d $(VENV) ]; then \
		python3 -m venv $(VENV); \
	fi
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
	fi
	$(PIP) install --upgrade pip -q
	$(PIP) install -r requirements.txt -q
	$(PYTHON) app.py

## 가상환경 삭제
clean:
	rm -rf $(VENV)
