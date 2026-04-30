# ユニットテスト実行手順書

## テスト実行コマンド

```bash
# 全テスト実行（カバレッジ付き）
python -m pytest tests/ --cov=src --cov-report=term-missing -v

# ユニットテストのみ
python -m pytest tests/ -m unit -v

# インテグレーションテストのみ
python -m pytest tests/ -m integration -v

# 特定テストファイル
python -m pytest tests/unit/test_validators.py -v
```

## テスト構成

| テストファイル | テスト数 | 対象モジュール |
|--------------|---------|--------------|
| test_validators.py | 24 | 入力バリデーション（BVA含む） |
| test_validators_status.py | 11 | ステータスバリデーション |
| test_dal_auth.py | 13 | 認証・ロール判定 |
| test_dal_inventory.py | 5 | 在庫データアクセス |
| test_dal_orders.py | 7 | 発注提案データアクセス |
| test_dal_delivery.py | 5 | 配送データアクセス |
| test_components.py | 10 | UIコンポーネント |
| test_app.py | 14 | アプリメイン処理 |
| test_pages_dashboard.py | 3 | ダッシュボードページ |
| test_pages_orders.py | 8 | 発注提案ページ |
| test_pages_delivery.py | 5 | 配送状況ページ |
| test_pages_driver.py | 6 | ドライバーページ |
| test_pages_consent.py | 3 | プライバシー同意画面 |
| **合計** | **122** | |

## 期待される結果

- **テスト数**: 122
- **通過**: 122 (100%)
- **失敗**: 0
- **カバレッジ**: 98.35%（目標: 80%以上）

## カバレッジ詳細

| モジュール | カバレッジ | 備考 |
|-----------|----------|------|
| src/utils/ | 100% | validators.py, constants.py |
| src/dal/ | 99%+ | auth, inventory, orders, delivery (session.py: 83%) |
| src/components/ | 100% | alerts, charts, common |
| src/pages/ | 97%+ | 全5ページ |
| src/app.py | 98% | メインエントリーポイント |
| **合計** | **98.35%** | |

## モック戦略
- **Snowpark Session**: `unittest.mock.MagicMock` でチェーン可能なDataFrameモックを作成
- **Streamlit**: `@patch("module.st")` でUI関数をモック
- **キャッシュ**: `conftest.py` の `_clear_st_cache` fixtureでテスト間のキャッシュをクリア

## 失敗時の対処
1. `ruff check` でコードスタイル違反を確認
2. カバレッジ不足の場合は `--cov-report=term-missing` で未カバー行を確認
3. モック関連の失敗は `conftest.py` の `MockRow`, `make_mock_df` を確認
