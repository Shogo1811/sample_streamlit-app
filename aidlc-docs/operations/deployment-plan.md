# デプロイメント計画（v2 — Container Services）

## 1. 環境構成

| 環境 | ブランチ | データベース | Compute Pool | トリガー |
|------|----------|-------------|-------------|----------|
| DEV | ローカル | RAMEN_LOGISTICS_DEV_DB | - | 手動 |
| STG | develop | RAMEN_LOGISTICS_STG_DB | RAMEN_APP_STG_POOL | Push自動 |
| PROD | main | RAMEN_LOGISTICS_PROD_DB | RAMEN_APP_PROD_POOL | Push→手動承認 |

## 2. Azure AD セットアップ手順

### 2.1 アプリ登録（Azure Portal → Entra ID）

1. **Azure Portal** → Microsoft Entra ID → アプリの登録 → 新規登録
   - 名前: `ramen-logistics`
   - サポートされるアカウントの種類: この組織のディレクトリのみ
   - リダイレクト URI (SPA): `https://<SPCS_ENDPOINT_URL>/`
2. 登録後、以下を控える:
   - **アプリケーション (クライアント) ID** → `AZURE_AD_CLIENT_ID`
   - **ディレクトリ (テナント) ID** → `AZURE_AD_TENANT_ID`
3. **API の公開** → スコープ追加
   - スコープ名: `access_as_user`
   - 同意できるのは: 管理者とユーザー
4. **マニフェスト** → `"groupMembershipClaims": "SecurityGroup"` に変更
   （JWTにgroupsクレームを含める）

### 2.2 セキュリティグループ作成

1. **Entra ID** → グループ → 新しいグループ
   - グループ名: `ramen-logistics-managers`
   - メンバー: 店長ユーザーを追加
   - → **オブジェクトID** を控える → `AZURE_AD_MANAGER_GROUP_ID`
2. 同様に `ramen-logistics-drivers` グループを作成
   - メンバー: ドライバーユーザーを追加
   - → **オブジェクトID** を控える → `AZURE_AD_DRIVER_GROUP_ID`

### 2.3 Snowflake USER_ROLE_MAPPING 更新

Azure AD ユーザーの **oid** を USER_ROLE_MAPPING の USER_ID に登録:

```sql
-- 例: 店長ユーザー
INSERT INTO APP.USER_ROLE_MAPPING (USER_ID, ROLE_TYPE, RELATED_ID)
VALUES ('<Azure AD oid>', 'MANAGER', 1);

-- 例: ドライバーユーザー
INSERT INTO APP.USER_ROLE_MAPPING (USER_ID, ROLE_TYPE, RELATED_ID)
VALUES ('<Azure AD oid>', 'DRIVER', 1);
```

### 2.4 環境変数設定

#### ローカル開発 (.env)
```
AZURE_AD_TENANT_ID=<テナントID>
AZURE_AD_CLIENT_ID=<クライアントID>
AZURE_AD_MANAGER_GROUP_ID=<店長グループID>
AZURE_AD_DRIVER_GROUP_ID=<ドライバーグループID>
```

#### フロントエンド (.env.local → frontend/)
```
VITE_AZURE_AD_TENANT_ID=<テナントID>
VITE_AZURE_AD_CLIENT_ID=<クライアントID>
```

#### Snowflake Secrets
```sql
-- Azure AD Secrets 更新
ALTER SECRET APP.AZURE_AD_SECRETS SET SECRET_STRING =
  '{"tenant_id":"<テナントID>","client_id":"<クライアントID>","manager_group_id":"<店長グループID>","driver_group_id":"<ドライバーグループID>"}';
```

#### GitHub Actions Secrets
| Secret名 | 値 |
|-----------|-----|
| SNOWFLAKE_ACCOUNT | Snowflakeアカウント識別子 |
| SNOWFLAKE_USER | CI/CDサービスアカウント |
| SNOWFLAKE_PRIVATE_KEY | キーペア認証の秘密鍵（PEM） |

## 3. 初回デプロイ手順

### Step 1: Snowflake インフラ構築
```bash
# ACCOUNTADMINで実行
export ENV=PROD AUTO_SUSPEND_SEC=180
envsubst < sql/setup_container_services.sql | snowsql -f -
```

### Step 2: サービスアカウント作成
```sql
CREATE USER RAMEN_SVC_USER
    PASSWORD = '<secure-password>'
    DEFAULT_ROLE = RAMEN_SVC_ROLE
    DEFAULT_WAREHOUSE = RAMEN_APP_PROD_WH;
GRANT ROLE RAMEN_SVC_ROLE TO USER RAMEN_SVC_USER;
```

### Step 3: Docker イメージ ビルド & Push
```bash
# Image Repository URL 取得
snow sql -q "SHOW IMAGE REPOSITORIES IN SCHEMA APP"

# ログイン & Push
snow registry login
docker build -t <REPO_URL>/ramen-logistics:v2.0.0 -f docker/Dockerfile .
docker push <REPO_URL>/ramen-logistics:v2.0.0
```

### Step 4: Service 作成
```sql
CREATE SERVICE APP.RAMEN_LOGISTICS_SERVICE
    IN COMPUTE POOL RAMEN_APP_PROD_POOL
    FROM SPECIFICATION_FILE = 'spec.yml'
    EXTERNAL_ACCESS_INTEGRATIONS = (AZURE_AD_ACCESS)
    MIN_INSTANCES = 1
    MAX_INSTANCES = 1;
```

### Step 5: エンドポイント確認
```sql
SHOW ENDPOINTS IN SERVICE APP.RAMEN_LOGISTICS_SERVICE;
-- → ingress_url をAzure ADのリダイレクトURIに登録
```

### Step 6: Azure AD リダイレクトURI更新
- Azure Portal → アプリの登録 → リダイレクト URI に `https://<ingress_url>/` を追加

## 4. CI/CD パイプライン

```
Push to develop → lint → test → security → Docker build → Push → Deploy STG → Wait READY
Push to main    → lint → test → security → Docker build → Push → Deploy PROD → Wait READY
                                                                    ↑ 手動承認
```

### パイプライン構成
| ジョブ | 内容 |
|--------|------|
| lint-backend | ruff check + format (Python) |
| lint-build-frontend | tsc --noEmit + vite build (TypeScript) |
| test-backend | pytest 50テスト |
| security | pip-audit + ruff security rules |
| deploy-stg/prod | SQL適用 → Docker build → Image push → Service deploy → ヘルスチェック待機 |

## 5. 運用コマンド

```sql
-- サービス状態確認
SELECT SYSTEM$GET_SERVICE_STATUS('APP.RAMEN_LOGISTICS_SERVICE');

-- ログ確認
SELECT SYSTEM$GET_SERVICE_LOGS('APP.RAMEN_LOGISTICS_SERVICE', 0, 'ramen-logistics', 100);

-- サービス再起動
ALTER SERVICE APP.RAMEN_LOGISTICS_SERVICE SUSPEND;
ALTER SERVICE APP.RAMEN_LOGISTICS_SERVICE RESUME;

-- サービス停止（コスト削減）
ALTER SERVICE APP.RAMEN_LOGISTICS_SERVICE SUSPEND;
ALTER COMPUTE POOL RAMEN_APP_PROD_POOL SUSPEND;
```
