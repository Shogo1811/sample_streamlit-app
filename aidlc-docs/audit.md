# AI-DLC 監査ログ（v2 — 移行プロジェクト）

## 2026-04-28 - プロジェクト開始
- **種別**: 移行（Brownfield）
- **移行元**: Streamlit in Snowflake (SiS) アプリ（AI-DLC v1 全フェーズ完了済み）
- **移行先**: React (TypeScript) + FastAPI + Snowflake Container Services
- **ユーザーリクエスト**:
  - frontend/ と backend/ を新規作成（方法A）
  - 既存の sql/, src/dal/, src/utils/ は流用
  - 機能: 在庫確認・発注承認・配送管理のCRUD
  - 認証: Azure AD SSO
  - AI-DLCで実装
- **旧ドキュメント**: aidlc-docs/archive/v1-streamlit/ にアーカイブ

## 2026-04-28 - ワークスペース検出完了
- **プロジェクト種別**: Brownfield（移行）
- **既存コード**: Streamlit アプリ一式（src/, sql/, tests/, .github/）
- **次のステージ**: リバースエンジニアリング → 要件分析
