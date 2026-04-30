# AI-DLC 状態管理

## プロジェクト情報
- **プロジェクト種別**: 移行（Brownfield — Streamlit → React+FastAPI+Container Services）
- **開始日**: 2026-04-28
- **現在のステージ**: CONSTRUCTION — ビルドとテスト完了、レビュー待ち
- **前バージョン**: aidlc-docs/archive/v1-streamlit/

## ワークスペース状態
- **既存コード**: あり（Streamlit アプリ v1 — 全フェーズ完了済み）
- **リバースエンジニアリング**: 実施（既存コードの構造・機能を分析済み）
- **ワークスペースルート**: （プロジェクトルート）

## 移行方針
- **方法**: 方法A（frontend/ と backend/ を新規作成）
- **流用対象**: sql/, src/dal/, src/utils/
- **新規**: frontend/ (React TS), backend/ (FastAPI)
- **認証変更**: Snowflake Roles → Azure AD SSO
- **デプロイ変更**: Streamlit in Snowflake → Snowflake Container Services

## コード配置ルール
- **アプリケーションコード**: ワークスペースルート（aidlc-docs/ には配置しない）
- **ドキュメント**: aidlc-docs/ のみ
- **構造パターン**: frontend/, backend/ 分離構成

## 拡張機能設定
| 拡張機能 | 有効 | 決定時点 |
|---|---|---|
| セキュリティベースライン | はい | 要件分析 Q9 |
| プロパティベーステスト | はい | 要件分析 Q9 |

## ステージ進捗
### INCEPTION フェーズ
- [x] ワークスペース検出 - Brownfield移行プロジェクトとして識別
- [x] リバースエンジニアリング - 完了（4ドキュメント作成）
- [x] 要件分析 - 完了（9問回答、全A、矛盾なし）
- [x] ユーザーストーリー - SKIP（v1ストーリー有効、技術移行のためユーザー要件同一）
- [x] アプリケーション設計 - SKIP（要件定義書で十分）
- [x] ユニット生成 - 完了（3ユニット: backend, frontend, infrastructure）
- [x] ワークフロー計画 - 完了
### CONSTRUCTION フェーズ
- [x] 機能設計 - 完了（API設計、スキーマ定義）
- [x] NFR要件 - SKIP（要件定義書で網羅済み）
- [x] NFR設計 - SKIP
- [x] インフラ設計 - 完了（Dockerfile, nginx.conf, spec.yml）
- [x] コード生成 - 完了（backend 15ファイル, frontend 15ファイル, infra 5ファイル）
- [x] ビルドとテスト - 完了（21テスト全通過、リンター全クリア）
### OPERATIONS フェーズ
- [ ] デプロイメント計画

## 現在のステータス
- 2026-04-28: AI-DLC v2 開始。Streamlit→React+FastAPI+Container Services移行プロジェクト。
