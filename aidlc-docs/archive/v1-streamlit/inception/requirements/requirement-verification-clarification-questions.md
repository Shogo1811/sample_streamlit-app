# Requirements Clarification Questions

回答内容にいくつか確認が必要な点がありました。以下の質問に回答をお願いします。

---

## Ambiguity 1: デプロイ先と認証方式の整合性
Q6で「Snowflake内でデプロイ」（Streamlit in Snowflake / SiS）を選択されましたが、Q5で「Streamlit built-in パスワード認証」を選択されています。
Streamlit in Snowflake（SiS）では、認証はSnowflakeのユーザー管理で行われるため、Streamlit built-inのパスワード認証（`st.secrets`ベース）は利用できません。

### Clarification Question 1
SiS環境での認証はどのようにしますか？

A) Snowflakeのユーザー認証をそのまま利用する（Snowflake側でユーザーを作成・管理）
B) Snowflakeのロール機能で店長用・ドライバー用にアクセス権限を分離する
C) SiSではなく、通常のStreamlitアプリとしてデプロイし直す（Streamlit built-inパスワード認証を使用）
X) Other (please describe after [Answer]: tag below)

[Answer]:B

## Ambiguity 2: 自動発注の具体的な仕組み
Q1で「ラーメンチェーン店の食材等の自動発注」とありますが、「自動発注」の仕組みについて詳細を教えてください。

### Clarification Question 2
自動発注のロジックはどのようなものを想定していますか？

A) ルールベース — 在庫が閾値を下回ったら自動的に発注を作成する
B) AI予測ベース — 過去の消費データから需要を予測し、自動発注を作成する
C) 手動 + 提案 — システムが発注提案を表示し、店長が承認して発注する
D) スケジュールベース — 定期的（毎日/毎週）に固定量を自動発注する
X) Other (please describe after [Answer]: tag below)

[Answer]:CとD

## Ambiguity 3: 初期リリースのスコープ
Q1で目的は「自動発注」、Q7で初期リリースの最重要機能は「データのリアルタイム可視化」と回答されています。
初期リリースに自動発注機能を含めるかどうかを確認させてください。

### Clarification Question 3
初期リリースのスコープはどこまでですか？

A) 可視化のみ — まず在庫・配送データの可視化ダッシュボードを作り、自動発注は将来フェーズで追加
B) 可視化 + 発注提案 — 可視化に加え、発注が必要な食材の提案表示まで含める（実際の発注実行は将来フェーズ）
C) フル機能 — 可視化 + 自動発注の両方を初期リリースに含める
X) Other (please describe after [Answer]: tag below)

[Answer]:B

## Ambiguity 4: 配送業者ドライバーの利用シーン
Q2で配送業者のドライバーも対象ユーザーとのことですが、ドライバーがこのアプリで何をするか教えてください。

### Clarification Question 4
配送業者のドライバーはこのアプリで何を行いますか？

A) 配送先・配送スケジュールの確認のみ（閲覧専用）
B) 配送完了の報告・ステータス更新
C) 配送先の確認 + 配送完了報告の両方
D) ドライバーは初期リリースでは対象外（将来フェーズで対応）
X) Other (please describe after [Answer]: tag below)

[Answer]:C
