.DEFAULT_GOAL := help

.PHONY: help setup sync test test-unit lint fmt fmt-check type check hooks serve serve-sse docker-build docker-up docker-down

help: ## 利用可能なコマンド一覧
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: sync ## 初回セットアップ（依存 + pre-commit）
	uv run pre-commit install

sync: ## 依存関係を同期
	uv sync --all-extras

test: ## 全テスト（カバレッジ付き）
	uv run pytest

test-unit: ## ユニットテストのみ（高速）
	uv run pytest tests/unit/ -q

lint: ## Lint（CI と一致）
	uv run ruff check .

fmt: ## フォーマット適用
	uv run ruff format .

fmt-check: ## フォーマットチェック（CI と一致）
	uv run ruff format --check .

type: ## 型チェック（CI と一致）
	uv run mypy

check: lint fmt-check type test ## CI 相当の一括検証

hooks: ## pre-commit 全フック実行
	uv run pre-commit run --all-files

serve: ## MCP サーバー（stdio）
	uv run formaforge serve

serve-sse: ## MCP サーバー（SSE）
	uv run formaforge serve --transport sse --host 127.0.0.1 --port 8000

docker-build: ## Docker イメージをビルド
	docker compose build

docker-up: ## Docker Compose で起動
	docker compose up --build

docker-down: ## Docker Compose を停止
	docker compose down
