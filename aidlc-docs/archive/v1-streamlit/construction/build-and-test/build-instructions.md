# ビルド手順書

## 前提条件
- Python >= 3.9
- pip（パッケージマネージャ）
- Snowflake Snowpark Python SDK >= 1.11.0
- Streamlit >= 1.31.0

## 依存関係インストール

```bash
# 本番依存 + 開発依存を一括インストール
pip install -e ".[dev]"
```

### 主要依存関係

| パッケージ | バージョン | 用途 |
|-----------|-----------|------|
| snowflake-snowpark-python | >=1.11.0,<2.0 | Snowflake接続・DataFrame API |
| streamlit | >=1.31.0,<2.0 | Web UI フレームワーク |
| ruff | >=0.4.0 | リンター・フォーマッター |
| pytest | >=8.0 | テストフレームワーク |
| pytest-cov | >=5.0 | カバレッジ計測 |

## ビルド検証

```bash
# Pythonインポート確認
python -c "from snowflake.snowpark import Session; import streamlit as st; print('OK')"

# リンター
ruff check src/ tests/

# フォーマッター
ruff format --check src/ tests/
```

## 期待される成果物
- `src/` — アプリケーションコード（app.py, pages/, dal/, components/, utils/）
- `tests/` — ユニットテスト（122テスト）
- `sql/` — Snowflake DDL/DML（setup.sql, seed.sql等）
- `.github/workflows/ci-cd.yml` — CI/CDパイプライン
- `pyproject.toml` — プロジェクト設定

## トラブルシューティング
- `snowflake-snowpark-python` インストール失敗: Python 3.9〜3.11を使用すること
- `streamlit` バージョン競合: `pip install --upgrade pip` 後に再試行
