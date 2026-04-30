# 要件定義書（v2 — 移行プロジェクト）

## 1. プロジェクト概要

### 目的
既存のStreamlit in Snowflake (SiS) アプリを **React (TypeScript) + FastAPI + Snowflake Container Services** に移行する。

### 背景
- 既存アプリは AI-DLC v1 で開発完了済み（122テスト、カバレッジ98%）
- Streamlit の UI 制約（カスタマイズ性、レスポンシブ対応）を解消
- Azure AD SSO によるエンタープライズ認証への移行
- Snowflake Container Services による柔軟なデプロイ

### スコープ
- **移行対象**: 全機能（在庫確認・発注承認・配送管理の CRUD）
- **移行方式**: 一括移行（全機能を同時に実装）
- **流用**: sql/, src/dal/, src/utils/（バックエンド側で再利用）
- **新規作成**: frontend/ (React TS), backend/ (FastAPI)

---

## 2. 機能要件（FR）

既存の機能要件を維持しつつ、アーキテクチャを変更する。

### FR-01〜05: 在庫確認ダッシュボード
- 店舗別在庫のリアルタイム可視化（棒グラフ・折線グラフ）
- カテゴリフィルタリング
- 閾値ベースの低在庫アラート
- **変更点**: Altair → MUI Charts or Recharts、Streamlit → React コンポーネント

### FR-06〜10: 発注承認ワークフロー
- 発注提案一覧表示（ステータスフィルタ）
- 承認/却下操作（2フェーズ確認 → MUI Dialog）
- カスタム数量入力
- 承認済み発注予定一覧
- **変更点**: st.session_state → React state + API 呼出

### FR-11〜14: 配送管理
- ドライバー向け配送一覧（モバイル最適化）
- 配送完了報告
- 店長向け配送ステータス監視
- **変更点**: Streamlit モバイルCSS → MUI レスポンシブ

### FR-15: 認証・認可（新規）
- Azure AD SSO ログイン（MSAL.js）
- JWT トークン検証（FastAPI）
- Azure AD グループベースのロールマッピング
- **廃止**: Snowflake CURRENT_USER() ベースの認証

### FR-16: プライバシー同意（維持）
- プライバシーポリシー表示・同意取得
- 同意履歴管理
- **変更点**: Streamlit UI → React MUI Dialog

---

## 3. 非機能要件（NFR）

### NFR-01: パフォーマンス
- API レスポンス: 200ms 以内（95パーセンタイル）
- 初回ページロード: 3秒以内
- ダッシュボードデータ更新: 5分間隔キャッシュ

### NFR-02: セキュリティ
- Azure AD SSO（OIDC / OAuth 2.0）
- JWT トークン検証（FastAPI ミドルウェア）
- CORS 設定（同一コンテナ内は localhost）
- HTTPS 必須（Container Services Ingress）
- サービスアカウントによる Snowflake 接続
- アプリ層でのロールベースフィルタリング（RLS 代替）
- セキュリティベースライン拡張: 有効

### NFR-03: 可用性
- Snowflake Container Services のマネージド可用性
- コンテナヘルスチェック

### NFR-04: テスタビリティ
- Frontend: Vitest + React Testing Library
- Backend: pytest（既存テスト流用 + API テスト追加）
- プロパティベーステスト拡張: 有効
- カバレッジ目標: 80%以上

### NFR-05: デプロイアビリティ
- Docker マルチステージビルド
- Snowflake Container Services デプロイ
- 1コンテナ構成（Nginx + FastAPI）

### NFR-06: 監査
- 既存の AUDIT_LOG、CONSENT_RECORDS を維持
- API アクセスログの追加

---

## 4. アーキテクチャ決定

### 4.1 全体構成
```
┌─────────────────────────────────────────────┐
│  Snowflake Container Services               │
│  ┌────────────────────────────────────────┐  │
│  │  Docker Container                      │  │
│  │  ┌──────────┐    ┌──────────────────┐  │  │
│  │  │  Nginx   │───▶│   FastAPI        │  │  │
│  │  │(React静的│    │  ┌────────────┐  │  │  │
│  │  │ ファイル)│    │  │  DAL層     │  │  │  │
│  │  └──────────┘    │  │(既存流用)  │  │  │  │
│  │                  │  └─────┬──────┘  │  │  │
│  │                  └────────┼─────────┘  │  │
│  └───────────────────────────┼────────────┘  │
│                              │ Snowpark      │
│                    ┌─────────▼──────────┐    │
│                    │  Snowflake DB      │    │
│                    │  (Tables, SPs)     │    │
│                    └────────────────────┘    │
└─────────────────────────────────────────────┘
         ▲
         │ HTTPS (Azure AD JWT)
    ┌────┴────┐
    │ Browser │
    │(MSAL.js)│
    └─────────┘
```

### 4.2 フロントエンド（frontend/）
- **フレームワーク**: React + TypeScript + Vite
- **UIライブラリ**: MUI (Material UI)
- **状態管理**: React Query (TanStack Query) + useState
- **認証**: MSAL.js (@azure/msal-browser)
- **HTTP**: axios or fetch（React Query 経由）
- **チャート**: Recharts or MUI X Charts

### 4.3 バックエンド（backend/）
- **フレームワーク**: FastAPI
- **DB接続**: snowflake-snowpark-python（既存DAL流用）
- **認証**: JWT 検証ミドルウェア（Azure AD 公開鍵）
- **ロール管理**: Azure AD グループ → アプリ内ロールマッピング
- **データフィルタ**: アプリ層でユーザーロールに基づくフィルタリング

### 4.4 認証フロー
```
Browser → MSAL.js → Azure AD → Access Token
Browser → API Request (Bearer Token) → FastAPI
FastAPI → JWT 検証 → Azure AD Groups → ロール判定
FastAPI → サービスアカウント → Snowflake → データ取得（ロールでフィルタ）
```

---

## 5. ディレクトリ構成（予定）

```
sample_streamlit-app/
├── frontend/                  # React (TypeScript)
│   ├── src/
│   │   ├── components/        # MUI コンポーネント
│   │   ├── pages/             # ページコンポーネント
│   │   ├── hooks/             # カスタムフック
│   │   ├── services/          # API クライアント
│   │   ├── auth/              # MSAL 認証
│   │   ├── types/             # TypeScript 型定義
│   │   └── utils/             # ユーティリティ
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/                   # FastAPI
│   ├── app/
│   │   ├── main.py            # FastAPI エントリポイント
│   │   ├── routers/           # APIルーター
│   │   ├── middleware/        # 認証ミドルウェア
│   │   ├── dependencies/      # DI（セッション、認証）
│   │   └── schemas/           # Pydantic スキーマ
│   ├── requirements.txt
│   └── tests/
├── src/dal/                   # 流用（Snowpark DAL）
├── src/utils/                 # 流用（定数・バリデーション）
├── sql/                       # 流用（DDL/SP）
├── docker/
│   ├── Dockerfile             # マルチステージビルド
│   └── nginx.conf             # Nginx 設定
├── spec.yml                   # Container Services 仕様
└── pyproject.toml             # 更新
```

---

## 6. 流用計画

| 既存モジュール | 流用方法 | 変更点 |
|---|---|---|
| src/dal/session.py | backend/ から import | SiS自動検出を廃止、サービスアカウント接続に変更 |
| src/dal/auth.py | 部分流用 | CURRENT_USER() → Azure AD ユーザーID、同意管理は維持 |
| src/dal/inventory.py | ほぼそのまま | st.cache_data → FastAPI キャッシュ（functools.lru_cache等） |
| src/dal/orders.py | ほぼそのまま | st.cache_data 廃止、SP呼出ロジックは維持 |
| src/dal/delivery.py | そのまま | 変更なし（元々キャッシュなし） |
| src/utils/constants.py | そのまま | 変更なし |
| src/utils/validators.py | そのまま | 変更なし |
| sql/setup.sql | 流用 | RLS の CURRENT_USER() 参照を調整（セッション変数 or 廃止） |
| sql/seed.sql | 流用 | Azure AD ユーザーIDに対応するテストデータ追加 |

---

## 7. リスク評価

| リスク | 影響 | 対策 |
|---|---|---|
| RLS廃止によるセキュリティ低下 | 高 | FastAPI ミドルウェアで厳密なフィルタリング、テストで検証 |
| 1コンテナ構成のスケーラビリティ | 中 | 初期は1コンテナ、必要に応じ分離可能な設計 |
| Azure AD テナント未準備 | 中 | モック認証で開発可能、テナント情報は後から差し込み |
| 一括移行のリスク | 中 | 既存テスト流用 + 新規テストで品質担保 |
