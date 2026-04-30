# 技術スタック分析

## 現行スタック
| カテゴリ | 技術 | バージョン |
|---|---|---|
| 言語 | Python | >=3.9 |
| フレームワーク | Streamlit | >=1.31.0, <2.0 |
| DB接続 | snowflake-snowpark-python | >=1.11.0, <2.0 |
| DB | Snowflake | - |
| リンター | ruff | >=0.4.0 |
| テスト | pytest | >=8.0 |
| カバレッジ | pytest-cov | >=5.0 |
| CI/CD | GitHub Actions | - |
| デプロイ | Streamlit in Snowflake (SiS) | - |

## 移行先スタック（予定）
| カテゴリ | 技術 | 備考 |
|---|---|---|
| Frontend 言語 | TypeScript | - |
| Frontend FW | React | Vite ベース想定 |
| Backend 言語 | Python | 既存DAL流用のため |
| Backend FW | FastAPI | - |
| DB接続 | snowflake-snowpark-python | 流用 |
| DB | Snowflake | 流用 |
| 認証 | Azure AD (Entra ID) | MSAL / OIDC |
| デプロイ | Snowflake Container Services | Docker コンテナ |
| コンテナ | Docker | multi-stage build |

## 流用可能なコード
| パス | 内容 | 流用方法 |
|---|---|---|
| src/dal/session.py | Snowpark セッション管理 | FastAPI 起動時に初期化（SiS自動検出は不要に） |
| src/dal/auth.py | ロール取得・同意管理 | Azure AD連携に書き換え。同意管理は流用可能 |
| src/dal/inventory.py | 在庫CRUD | ほぼそのまま流用（キャッシュ方式変更） |
| src/dal/orders.py | 発注CRUD | ほぼそのまま流用（キャッシュ方式変更） |
| src/dal/delivery.py | 配送CRUD | ほぼそのまま流用 |
| src/utils/constants.py | 定数・Enum | そのまま流用 |
| src/utils/validators.py | バリデーション | そのまま流用 |
| sql/*.sql | DDL/SP/RLS | 流用（認証部分のRAPは要調整） |

## 流用不可（書き直し）
| パス | 理由 |
|---|---|
| src/app.py | Streamlit 固有のルーティング |
| src/pages/*.py | Streamlit UI → React コンポーネントに |
| src/components/*.py | Streamlit UI部品 → React コンポーネントに |
| streamlit_app.py | SiS エントリポイント |
| .streamlit/ | Streamlit 設定 |
