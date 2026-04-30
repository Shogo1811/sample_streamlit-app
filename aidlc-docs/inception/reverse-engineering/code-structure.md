# コード構造分析

## ディレクトリ構成
```
sample_streamlit-app/
├── streamlit_app.py          # SiSエントリポイント（src.app.main呼出）
├── src/
│   ├── app.py                # メインルーティング（認証→同意→ロール→ページ振分）
│   ├── dal/                  # データアクセス層
│   │   ├── session.py        # Snowpark Session 管理（SiS/ローカル自動判定）
│   │   ├── auth.py           # 認証・ロール・同意（CURRENT_USER, RBAC）
│   │   ├── inventory.py      # 在庫CRUD（キャッシュ付き）
│   │   ├── orders.py         # 発注提案・承認CRUD（SP呼出）
│   │   └── delivery.py       # 配送CRUD（キャッシュなし — リアルタイム）
│   ├── pages/                # UI ページ
│   │   ├── manager_dashboard.py  # ダッシュボード（チャート、フィルタ、アラート）
│   │   ├── manager_orders.py     # 発注提案管理（承認/却下ワークフロー）
│   │   ├── manager_delivery.py   # 配送状況一覧（店長向け）
│   │   ├── driver_delivery.py    # 配送管理（ドライバー向け、モバイル最適化）
│   │   └── privacy_consent.py    # プライバシー同意画面
│   ├── components/           # 再利用UI部品
│   │   ├── alerts.py         # 低在庫アラート
│   │   ├── charts.py         # Altair チャート（棒/折線）
│   │   └── common.py         # 共通UI（ローディング、エラー、空状態）
│   └── utils/                # ユーティリティ
│       ├── constants.py      # ステータスEnum、遷移ルール、TTL、ロール
│       └── validators.py     # 入力バリデーション（数量、ステータス）
├── sql/
│   ├── setup.sql             # メインDDL（テーブル、RLS、SP）
│   ├── setup_dev.sql         # 開発環境DDL
│   ├── setup_prod.sql        # 本番環境DDL
│   └── seed.sql              # テストデータ
├── tests/
│   ├── conftest.py           # テストフィクスチャ（MockRow, make_mock_df）
│   └── unit/                 # ユニットテスト（122テスト、カバレッジ98%）
├── pyproject.toml            # 依存関係・リンター・テスト設定
├── snowflake.yml             # Snowflake CLI 設定
└── .github/workflows/ci-cd.yml  # CI/CD パイプライン
```

## モジュール間依存関係
```
app.py
  ├── dal/session.py          # セッション取得
  ├── dal/auth.py             # 認証・ロール判定
  ├── pages/privacy_consent.py # 同意未取得時
  ├── pages/manager_*.py      # 店長ロール時
  └── pages/driver_delivery.py # ドライバーロール時

pages/manager_dashboard.py
  ├── dal/inventory.py        # 在庫データ取得
  ├── components/charts.py    # チャート描画
  ├── components/alerts.py    # 低在庫アラート
  └── components/common.py    # ローディング等

pages/manager_orders.py
  ├── dal/orders.py           # 発注CRUD
  ├── utils/validators.py     # 数量バリデーション
  └── utils/constants.py      # ステータス定数

pages/driver_delivery.py
  ├── dal/delivery.py         # 配送CRUD
  └── utils/constants.py      # ステータス定数
```

## 主要パターン
1. **2フェーズ確認**: ボタン押下→session_state→rerun→確認UI→実行
2. **キャッシュ戦略**: マスタ1h / ダッシュボード5min / 認証5min / 配送なし
3. **SP呼出パターン**: session.call() → JSON解析 → 成否判定 → キャッシュクリア
4. **エラーハンドリング**: 接続/権限/書込/タイムアウトの4パターン
