# デプロイメント計画

## 1. デプロイフロー概要

```
開発者 → git push → GitHub Actions → Snowflake (SiS)

  develop ブランチ push
    → lint → test → security → deploy-stg（自動）

  main ブランチ push
    → lint → test → security → [手動承認] → deploy-prod
```

## 2. 環境構成

| 環境 | ブランチ | DB名 | WH名 | デプロイ方式 |
|------|---------|------|------|------------|
| STG | develop | RAMEN_LOGISTICS_STG_DB | RAMEN_APP_STG_WH | 自動（push時） |
| PROD | main | RAMEN_LOGISTICS_PROD_DB | RAMEN_APP_PROD_WH | 手動承認後自動 |

## 3. 前提条件（初回セットアップ）

### 3.1 Snowflake側
1. **アカウント準備**: Snowflakeアカウントが利用可能であること
2. **初回SQL実行**: 各環境でsetup.sqlを手動実行（DB・スキーマ・テーブル・SP・RAP作成）
   ```bash
   # STG環境
   export ENV=STG AUTO_SUSPEND_SEC=120 TIME_TRAVEL_DAYS=3 CREDIT_QUOTA=10
   envsubst < sql/setup.sql | snowsql -f -

   # PROD環境
   export ENV=PROD AUTO_SUSPEND_SEC=180 TIME_TRAVEL_DAYS=7 CREDIT_QUOTA=50
   envsubst < sql/setup.sql | snowsql -f -
   ```
3. **初期データ投入**（STGのみ）:
   ```bash
   export ENV=STG
   envsubst < sql/seed.sql | snowsql -f -
   ```
4. **Snowflake Tasks起動**: SP実装確認後にRESUME
   ```sql
   ALTER TASK APP.TASK_GENERATE_PROPOSALS RESUME;
   ALTER TASK APP.TASK_CLEANUP_DATA RESUME;
   ```

### 3.2 GitHub側
1. **Secrets設定**（Settings → Secrets and variables → Actions）:
   | Secret名 | 説明 |
   |----------|------|
   | `SNOWFLAKE_ACCOUNT` | Snowflakeアカウント識別子 |
   | `SNOWFLAKE_USER` | デプロイ用ユーザー名 |
   | `SNOWFLAKE_PRIVATE_KEY` | キーペア認証の秘密鍵（PEM形式） |

2. **Environments設定**:
   - `staging`: 自動デプロイ（保護ルールなし）
   - `production`: Required reviewers（承認者を設定）

3. **ブランチ保護ルール**:
   - `main`: Require PR、Require status checks (lint, test, security)
   - `develop`: Require status checks (lint, test)

## 4. 通常のデプロイ手順

### 4.1 開発 → STGデプロイ
```bash
# 機能ブランチで開発
git checkout -b feature/xxx develop
# ... コード変更 ...
git push origin feature/xxx

# PRを作成してdevelopにマージ
gh pr create --base develop
# → マージ後、自動でSTGにデプロイ
```

### 4.2 STG → PRODデプロイ
```bash
# developからmainへPR作成
gh pr create --base main --head develop

# → マージ後、GitHub Environment承認待ち
# → 承認者がApprove → 自動でPRODにデプロイ
```

## 5. SQL変更のデプロイ

CI/CDパイプラインは `sql/` ディレクトリの変更を自動検知し、`setup.sql` を `envsubst` 経由で適用します。

- `CREATE IF NOT EXISTS` / `CREATE OR REPLACE` により冪等実行
- SP定義は `CREATE OR REPLACE` で毎回再作成（安全）
- テーブル構造変更（ALTER TABLE）は手動で個別マイグレーションSQLを作成・実行

## 6. ロールバック手順

### Streamlitアプリのロールバック
```bash
# 前のコミットに戻してpush
git revert HEAD
git push origin main  # → 自動デプロイで前バージョンに復元
```

### SQL変更のロールバック
- Snowflake Time Travel（最大7日間）で復元可能
  ```sql
  -- テーブルデータの復元
  CREATE TABLE APP.TABLE_RESTORED CLONE APP.TABLE_NAME AT(OFFSET => -3600);
  ```
- SP定義のロールバックはgit revertでsetup.sqlを戻し、再デプロイ

## 7. 監視

| 項目 | 方法 |
|------|------|
| アプリ稼働状況 | Snowflake UI → Streamlit Apps |
| クエリパフォーマンス | Snowflake Query History |
| Warehouse利用量 | Resource Monitor（CREDIT_QUOTA設定済み） |
| Task実行状況 | `SHOW TASKS IN SCHEMA APP;` |
| CI/CD状況 | GitHub Actions タブ |

## 8. 本番デプロイ前チェックリスト

- [ ] プライバシーポリシーの事業者情報がプレースホルダーから実値に置換済み
- [ ] GitHub Secrets（SNOWFLAKE_ACCOUNT, USER, PRIVATE_KEY）が設定済み
- [ ] GitHub Environment `production` に承認者が設定済み
- [ ] Snowflake初回セットアップ（setup.sql）が実行済み
- [ ] Snowflake Tasks がRESUME済み
- [ ] STG環境で動作確認完了
