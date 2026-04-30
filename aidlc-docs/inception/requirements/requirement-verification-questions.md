# 要件確認質問（移行プロジェクト）

既存のStreamlitアプリをReact+FastAPIに移行するにあたり、以下を確認させてください。

---

## Q1. Frontend UIフレームワーク

React のUIコンポーネントライブラリはどれを使用しますか？

A) MUI (Material UI) — Google Material Design 準拠、豊富なコンポーネント
B) Ant Design — エンタープライズ向け、テーブル・フォームが充実
C) Chakra UI — 軽量・アクセシブル、柔軟なスタイリング
D) shadcn/ui + Tailwind CSS — コピー&ペースト型、フル制御可能
E) その他（具体的に指定してください）

[Answer]:A

---

## Q2. 状態管理

React の状態管理ライブラリはどれを使用しますか？

A) React Query (TanStack Query) + useState — サーバー状態はReact Query、ローカル状態はuseState
B) Redux Toolkit + RTK Query — 大規模状態管理 + API連携
C) Zustand — 軽量グローバルストア
D) お任せ（プロジェクト規模に応じて最適なものを選定）
E) その他（具体的に指定してください）

[Answer]:A

---

## Q3. Azure AD SSO 認証フロー

Azure AD 認証の実装方式はどれですか？

A) Frontend MSAL.js でトークン取得 → FastAPI でJWT検証（SPA フロー）
B) Backend 側で OIDC Authorization Code Flow（サーバーサイドフロー）
C) Azure AD B2C を使用（外部ユーザー向け）
D) まだ Azure AD テナントが未準備（テナント情報は後から提供）
E) その他（具体的に指定してください）

[Answer]:A

---

## Q4. 既存ロールマッピングとの統合

現行は Snowflake USER_ROLE_MAPPING テーブルでロール管理しています。Azure AD 移行後のロール管理方式は？

A) Azure AD グループ → FastAPI でマッピング（AD側でロール管理）
B) 引き続き Snowflake USER_ROLE_MAPPING を使用（ADユーザーIDでマッピング）
C) FastAPI 側に独自のロール管理テーブルを追加
D) お任せ（既存との互換性を重視して選定）
E) その他（具体的に指定してください）

[Answer]:A

---

## Q5. Snowflake Container Services の構成

Container Services でのコンテナ構成はどうしますか？

A) フロント + バックエンドを1コンテナにまとめる（シンプル構成）
B) フロント（Nginx + React）とバックエンド（FastAPI）を別コンテナ（2サービス構成）
C) バックエンドのみコンテナ化、フロントは別ホスティング（Vercel, CloudFront等）
D) お任せ（Container Services のベストプラクティスに従う）
E) その他（具体的に指定してください）

[Answer]:A

---

## Q6. 既存の Row Access Policy (RLS)

現行は Snowflake RLS で CURRENT_USER() ベースのアクセス制御を実装しています。Container Services 移行後は？

A) サービスアカウントで接続 → FastAPI 側でロールベースフィルタリング（アプリ層制御）
B) ユーザーごとに Snowflake セッション変数を設定して RLS を維持
C) RLS を廃止し、FastAPI の認可ミドルウェアで完全にアプリ層制御
D) お任せ（セキュリティ要件を満たす最適な方式を選定）
E) その他（具体的に指定してください）

[Answer]:A

---

## Q7. 同時移行 vs 段階的移行

移行の進め方はどうしますか？

A) 一括移行 — 全機能を一度にReact+FastAPIで実装し、Streamlit版を置き換え
B) 段階的移行 — まずダッシュボード（閲覧系）→ 次に発注（書込系）→ 配送
C) 並行運用 — 新旧を並行稼働させ、機能ごとに切り替え
D) お任せ（リスクとスピードのバランスで判断）
E) その他（具体的に指定してください）

[Answer]:A

---

## Q8. テスト戦略

移行後のテスト方針はどうしますか？

A) Frontend: Vitest + React Testing Library、Backend: pytest（既存テスト流用+追加）
B) E2E テストも含める（Playwright or Cypress）
C) 既存の pytest テストは流用し、フロントのテストは最低限
D) お任せ（カバレッジ目標を維持しつつ最適な戦略を選定）
E) その他（具体的に指定してください）

[Answer]:A

---

## Q9. 拡張機能オプトイン

以下の拡張機能を有効化しますか？

### セキュリティベースライン
Azure AD SSO + Container Services 環境でのセキュリティ設計を強化します。
A) はい — 有効化する
B) いいえ — 不要

[Answer]:A

### プロパティベーステスト
バリデーション等のテストにプロパティベーステストを追加します。
A) はい — 有効化する
B) いいえ — 不要

[Answer]:A
