# コード生成計画（Part 1）

## 1. ファイル構成・モジュール分割

```
sample_streamlit-app/
├── src/
│   ├── app.py                        # メインエントリーポイント（ロール判定→ページルーティング）
│   ├── pages/
│   │   ├── manager_dashboard.py      # 店長: ダッシュボード（在庫状況・推移・配送状況）
│   │   ├── manager_orders.py         # 店長: 発注提案・承認
│   │   ├── manager_delivery.py       # 店長: 配送状況確認
│   │   ├── driver_delivery.py        # ドライバー: 配送リスト・完了報告
│   │   └── privacy_consent.py        # 共通: プライバシーポリシー同意画面
│   ├── dal/                          # データアクセス層（DAL）
│   │   ├── __init__.py
│   │   ├── session.py                # Snowparkセッション管理（get_active_session + cache）
│   │   ├── inventory.py              # 在庫データ取得（DataFrame API）
│   │   ├── orders.py                 # 発注提案データ取得・Stored Procedure呼出
│   │   ├── delivery.py               # 配送データ取得・Stored Procedure呼出
│   │   └── auth.py                   # ロール判定（ユーザーロールマッピングテーブル照合）
│   ├── components/                   # 再利用可能UIコンポーネント
│   │   ├── __init__.py
│   │   ├── charts.py                 # グラフ・チャートコンポーネント
│   │   ├── alerts.py                 # 在庫アラート表示
│   │   └── common.py                 # 共通UI（ローディング、空状態、エラー表示）
│   └── utils/
│       ├── __init__.py
│       ├── constants.py              # 定数（ステータス値、閾値、ロール名）
│       └── validators.py             # 入力バリデーション（NFR-09準拠）
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # pytestフィクスチャ（モックセッション等）
│   ├── unit/
│   │   ├── test_validators.py        # バリデーションテスト（BVA含む）
│   │   ├── test_dal_inventory.py     # 在庫DALテスト
│   │   ├── test_dal_orders.py        # 発注DALテスト
│   │   ├── test_dal_delivery.py      # 配送DALテスト
│   │   └── test_dal_auth.py          # 認証DALテスト
│   └── integration/
│       └── test_snowflake_rap.py      # Row Access Policyテスト（ステージング環境）
├── sql/
│   ├── setup.sql                     # Snowflakeインフラ設定DDL
│   ├── setup_dev.sql                 # DEV環境パラメータ
│   ├── setup_prod.sql                # PROD環境パラメータ
│   └── seed.sql                      # 初期データ（食材マスタ、閾値）
├── .github/
│   └── workflows/
│       └── ci-cd.yml                 # CI/CDパイプライン
├── pyproject.toml                    # 依存管理・ツール設定
├── .gitignore
├── .githooks/
│   └── pre-push
├── .claude/
│   ├── settings.json
│   └── commands/
├── scripts/
│   └── pre-push-checks.sh
├── CLAUDE.md
└── aidlc-docs/                       # AI-DLCドキュメント（コードではない）
```

### レイヤー責務

| レイヤー | 責務 | 依存方向 |
|---------|------|----------|
| **UI層** (`pages/`, `components/`) | Streamlit画面描画、ユーザー入力受付 | → DAL層 |
| **DAL層** (`dal/`) | Snowparkセッション管理、DataFrame取得、Stored Procedure呼出 | → Snowflake |
| **バリデーション** (`utils/validators.py`) | 入力値検証（NFR-09） | 独立 |
| **定数** (`utils/constants.py`) | ステータス値、ロール名等 | 独立 |

---

## 2. Stored Procedure一覧

| SP名 | 引数 | 戻り値 | 責務 | 権限モデル |
|------|------|--------|------|-----------|
| `SP_APPROVE_ORDER_PROPOSAL` | proposal_id (INT), approved_quantity (INT), user_id (VARCHAR) | JSON {success: BOOL, message: VARCHAR} | 発注提案の承認処理。ステータス遷移バリデーション（確認中→承認のみ許可）、数量バリデーション（1〜10,000整数）、発注予定レコード作成、監査ログ記録をアトミックに実行 | OWNER'S RIGHTS |
| `SP_REJECT_ORDER_PROPOSAL` | proposal_id (INT), user_id (VARCHAR) | JSON {success: BOOL, message: VARCHAR} | 発注提案の却下処理。ステータス遷移バリデーション（確認中→却下のみ許可）、監査ログ記録 | OWNER'S RIGHTS |
| `SP_COMPLETE_DELIVERY` | delivery_id (INT), user_id (VARCHAR) | JSON {success: BOOL, message: VARCHAR} | 配送完了報告。ステータス遷移バリデーション（配送中→配送完了のみ許可）、完了日時自動記録、監査ログ記録 | OWNER'S RIGHTS |
| `SP_GENERATE_ORDER_PROPOSALS` | — (Snowflake Tasks用) | INT (生成件数) | 在庫データと消費パターンに基づく発注提案の自動生成。過去N日間の平均消費量×リードタイム日数+安全在庫で推奨発注数を算出 | OWNER'S RIGHTS |
| `SP_CLEANUP_EXPIRED_DATA` | — (Snowflake Tasks用) | INT (処理件数) | NFR-16に基づくデータ保持期間管理。3年超の個人情報を匿名化 | OWNER'S RIGHTS |

### 共通ルール
- 全SPはOWNER'S RIGHTS（EXECUTE AS OWNER）で実行
- SP内でCURRENT_USER()とユーザーロールマッピングテーブルを照合して操作権限を検証
- 不正な状態遷移はRAISE例外（'INVALID_STATE_TRANSITION'）
- 全操作は監査ログテーブルへのINSERTを含む（アトミック）

---

## 3. 画面構成定義（テキストベースワイヤーフレーム）

### 3.1 app.py（エントリーポイント）

```
┌─────────────────────────────────────┐
│ [プライバシーポリシー同意チェック]     │
│   ├── 未同意 → privacy_consent.py    │
│   └── 同意済み                        │
│        ├── ロール判定（auth.py）       │
│        │   ├── MANAGER → 店長画面     │
│        │   └── DRIVER  → ドライバー画面│
│        └── 不明ロール → エラー表示     │
└─────────────────────────────────────┘
```

### 3.2 店長画面: ダッシュボード（manager_dashboard.py）

```
┌─────────────────────────────────────────────┐
│ [サイドバー]           │ [メインエリア]       │
│                        │                      │
│ ▼ フィルタ             │ ■ 在庫状況           │
│   期間: [日付ピッカー]  │   [棒グラフ/チャート]  │
│   食材: [ドロップダウン] │                      │
│                        │ ■ 在庫推移           │
│ ▼ ナビゲーション        │   [時系列折れ線グラフ] │
│   📊 ダッシュボード     │                      │
│   📝 発注提案          │ ■ 配送状況           │
│   🚚 配送状況          │   [ステータス別一覧]   │
│   📋 発注予定          │                      │
│                        │ ⚠️ 在庫アラート       │
│                        │   [閾値以下の食材一覧] │
└─────────────────────────────────────────────┘
```

### 3.3 店長画面: 発注提案（manager_orders.py）

```
┌─────────────────────────────────────────────┐
│ [サイドバー]           │ [メインエリア]       │
│ （共通ナビゲーション）  │                      │
│                        │ ■ 発注提案リスト      │
│                        │ ┌──────────────────┐ │
│                        │ │食材名 | 在庫 | 推奨 │ │
│                        │ │───────+──────+─── │ │
│                        │ │麺     | 20   | 100 │ │
│                        │ │  [数量入力] [承認][却下]│
│                        │ │チャーシュー| 5 | 50│ │
│                        │ │  [数量入力] [承認][却下]│
│                        │ └──────────────────┘ │
│                        │                      │
│                        │ ■ 承認済み発注予定     │
│                        │   [発注予定リスト表]   │
└─────────────────────────────────────────────┘
```

### 3.4 店長画面: 配送状況（manager_delivery.py）

```
┌─────────────────────────────────────────────┐
│ [サイドバー]           │ [メインエリア]       │
│ （共通ナビゲーション）  │                      │
│                        │ ■ 配送一覧            │
│                        │   [未配送] [配送中] [完了]│
│                        │   タブ切替             │
│                        │                      │
│                        │ ┌──────────────────┐ │
│                        │ │配送ID | 予定 | 状態│ │
│                        │ │───────+──────+─── │ │
│                        │ │001   | 10:00| 配送中│ │
│                        │ │002   | 14:00| 未配送│ │
│                        │ └──────────────────┘ │
└─────────────────────────────────────────────┘
```

### 3.5 ドライバー画面（driver_delivery.py）— スマートフォン最適化

```
┌──────────────────────┐
│  🚚 本日の配送        │
│  佐藤さん             │
│                       │
│ ┌───────────────────┐ │
│ │ 📍 ラーメン〇〇店  │ │
│ │ 予定: 10:00        │ │
│ │ [■■■ 配送完了 ■■■] │ │  ← 大型ボタン（画面幅全体）
│ └───────────────────┘ │
│                       │
│ ┌───────────────────┐ │
│ │ 📍 ラーメン△△店  │ │
│ │ 予定: 14:00        │ │
│ │ [■■■ 配送完了 ■■■] │ │
│ └───────────────────┘ │
│                       │
│ ✅ 完了: 3件          │
│ 📋 残り: 2件          │
└──────────────────────┘
単一カラム / 縦スクロール
```

### 3.6 プライバシーポリシー同意画面（privacy_consent.py）

```
┌──────────────────────────────────┐
│  プライバシーポリシー             │
│                                  │
│  ┌────────────────────────────┐  │
│  │ (ポリシー全文 - スクロール)  │  │
│  │ ...                        │  │
│  └────────────────────────────┘  │
│                                  │
│  ☐ 上記に同意します              │
│                                  │
│  [同意して利用を開始する]        │
└──────────────────────────────────┘
```
