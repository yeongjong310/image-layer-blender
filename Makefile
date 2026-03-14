.PHONY: help install install-dev install-build run test lint format clean build app

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

help: ## 사용 가능한 명령어 목록
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ─── 설치 ───────────────────────────────────────────

venv: ## 가상환경 생성
	@test -d $(VENV) || python3 -m venv $(VENV)

install: venv ## 프로젝트 설치 (editable)
	$(PIP) install -e .

install-dev: venv ## 개발 의존성 포함 설치
	$(PIP) install -e ".[dev]"

install-build: venv ## 빌드 의존성 포함 설치
	$(PIP) install -e ".[build]"

install-all: venv ## 모든 의존성 설치
	$(PIP) install -e ".[dev,build]"

# ─── 실행 ───────────────────────────────────────────

run: install ## GUI 앱 실행
	$(PYTHON) -m merge_image_layer.main

# ─── 개발 ───────────────────────────────────────────

test: install-dev ## 테스트 실행
	$(VENV)/bin/pytest tests/ -v

lint: install-dev ## 린트 검사
	$(VENV)/bin/ruff check src/ tests/

format: install-dev ## 코드 포맷팅
	$(VENV)/bin/ruff format src/ tests/

typecheck: install-dev ## 타입 체크
	$(VENV)/bin/mypy src/

# ─── 빌드 ───────────────────────────────────────────

build: install-build ## PyInstaller로 단일 실행파일 빌드
	$(VENV)/bin/pyinstaller \
		--noconfirm \
		--onefile \
		--windowed \
		--name "merge-image-layer" \
		src/merge_image_layer/main.py

app: install-build ## macOS .app 번들 빌드
	$(VENV)/bin/pyinstaller \
		--noconfirm \
		--onedir \
		--windowed \
		--name "이미지합성" \
		--osx-bundle-identifier "com.merge-image-layer.app" \
		src/merge_image_layer/main.py
	@echo ""
	@echo "✅ dist/이미지합성.app 생성 완료"

# ─── 정리 ───────────────────────────────────────────

clean: ## 빌드 산출물 정리
	rm -rf build/ dist/ *.spec
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

clean-all: clean ## 가상환경 포함 전체 정리
	rm -rf $(VENV)
