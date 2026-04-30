# アーキテクチャ分析

## 現行アーキテクチャ
```
┌─────────────────────────────┐
│  Streamlit in Snowflake     │
│  (SiS — 単一Pythonプロセス) │
│                             │
│  ┌───────────┐              │
│  │ UI Pages  │──────┐       │
│  └───────────┘      │       │
│  ┌───────────┐      ▼       │
│  │Components │  ┌───────┐   │
│  └───────────┘  │  DAL  │   │
│                 └───┬───┘   │
└─────────────────────┼───────┘
                      │ Snowpark
               ┌──────▼──────┐
               │  Snowflake  │
               │  (Tables,   │
               │   SPs, RLS) │
               └─────────────┘
```

## 層構成
| 層 | 責務 | ファイル |
|---|---|---|
| Entry | SiS/ローカル切替 | streamlit_app.py, src/app.py |
| Pages | UI表示・ユーザー操作 | src/pages/*.py |
| Components | 再利用可能UI部品 | src/components/*.py |
| DAL | データアクセス（Snowpark） | src/dal/*.py |
| Utils | バリデーション・定数 | src/utils/*.py |
| SQL | DDL/DML/SP/RLS | sql/*.sql |

## 主要な技術的特徴
- **認証**: Snowflake CURRENT_USER() + USER_ROLE_MAPPING テーブル
- **認可**: Row Access Policy（テーブルレベルRLS）
- **セッション**: Snowpark Session（SiS自動検出 / secrets.toml フォールバック）
- **キャッシュ**: st.cache_data（マスタ1h, ダッシュボード5min, 認証5min, 配送なし）
- **状態管理**: st.session_state（2フェーズ確認パターン）
- **SP実行**: EXECUTE AS OWNER（権限昇格パターン）

## 移行時の考慮点
- DAL層（src/dal/）は Snowpark 依存 → FastAPI 側で流用可能
- UI Pages は Streamlit 固有 → React で完全書き直し
- st.cache_data → サーバーサイドキャッシュ（Redis等）or API レスポンスキャッシュ
- st.session_state → React state + API セッション管理
- 認証は Snowflake Roles → Azure AD SSO に完全変更
