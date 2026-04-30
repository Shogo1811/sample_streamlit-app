-- ============================================================
-- Snowflake Container Services インフラ設定
-- 実行前提: ACCOUNTADMINロールで実行すること
-- 環境変数: ${ENV} = DEV / STG / PROD
-- ============================================================

USE DATABASE RAMEN_LOGISTICS_${ENV}_DB;

-- ------------------------------------------------------------
-- 1. Image Repository（Docker イメージ格納用）
-- ------------------------------------------------------------
CREATE IMAGE REPOSITORY IF NOT EXISTS APP.IMAGE_REPO;

-- イメージURL確認:
-- SHOW IMAGE REPOSITORIES IN SCHEMA APP;
-- → <org>-<account>.registry.snowflakecomputing.com/ramen_logistics_${ENV}_db/app/image_repo

-- ------------------------------------------------------------
-- 2. Compute Pool（コンテナ実行環境）
-- ------------------------------------------------------------
CREATE COMPUTE POOL IF NOT EXISTS RAMEN_APP_${ENV}_POOL
    MIN_NODES = 1
    MAX_NODES = 1
    INSTANCE_FAMILY = CPU_X64_XS
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = ${AUTO_SUSPEND_SEC};

-- ------------------------------------------------------------
-- 3. Secrets（認証情報）
-- ------------------------------------------------------------

-- Snowflake サービスアカウント認証情報
CREATE SECRET IF NOT EXISTS APP.RAMEN_LOGISTICS_SECRETS
    TYPE = GENERIC_STRING
    SECRET_STRING = '{"account":"${SNOWFLAKE_ACCOUNT}","user":"${SNOWFLAKE_SVC_USER}","password":"${SNOWFLAKE_SVC_PASSWORD}"}';

-- Azure AD 設定
CREATE SECRET IF NOT EXISTS APP.AZURE_AD_SECRETS
    TYPE = GENERIC_STRING
    SECRET_STRING = '{"tenant_id":"${AZURE_AD_TENANT_ID}","client_id":"${AZURE_AD_CLIENT_ID}","manager_group_id":"${AZURE_AD_MANAGER_GROUP_ID}","driver_group_id":"${AZURE_AD_DRIVER_GROUP_ID}"}';

-- ------------------------------------------------------------
-- 4. Network Rule + External Access Integration
--    （Azure AD JWKS エンドポイントへのアクセス許可）
-- ------------------------------------------------------------
CREATE OR REPLACE NETWORK RULE APP.AZURE_AD_NETWORK_RULE
    MODE = EGRESS
    TYPE = HOST_PORT
    VALUE_LIST = ('login.microsoftonline.com:443');

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION AZURE_AD_ACCESS
    ALLOWED_NETWORK_RULES = (APP.AZURE_AD_NETWORK_RULE)
    ENABLED = TRUE;

-- ------------------------------------------------------------
-- 5. Service（コンテナデプロイ）
-- ------------------------------------------------------------
-- ※ spec.yml をアップロード後に実行
-- ※ イメージを Image Repository に push 済みであること

-- CREATE SERVICE APP.RAMEN_LOGISTICS_SERVICE
--     IN COMPUTE POOL RAMEN_APP_${ENV}_POOL
--     FROM SPECIFICATION_FILE = 'spec.yml'
--     EXTERNAL_ACCESS_INTEGRATIONS = (AZURE_AD_ACCESS)
--     MIN_INSTANCES = 1
--     MAX_INSTANCES = 1;

-- サービス確認:
-- SHOW SERVICES IN SCHEMA APP;
-- SELECT SYSTEM$GET_SERVICE_STATUS('APP.RAMEN_LOGISTICS_SERVICE');
-- SELECT SYSTEM$GET_SERVICE_LOGS('APP.RAMEN_LOGISTICS_SERVICE', 0, 'ramen-logistics', 100);

-- エンドポイントURL確認:
-- SHOW ENDPOINTS IN SERVICE APP.RAMEN_LOGISTICS_SERVICE;

-- ------------------------------------------------------------
-- 6. サービスアカウント用ロール・権限
-- ------------------------------------------------------------
CREATE ROLE IF NOT EXISTS RAMEN_SVC_ROLE;

GRANT USAGE ON DATABASE RAMEN_LOGISTICS_${ENV}_DB TO ROLE RAMEN_SVC_ROLE;
GRANT USAGE ON SCHEMA APP TO ROLE RAMEN_SVC_ROLE;
GRANT USAGE ON SCHEMA AUDIT TO ROLE RAMEN_SVC_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA APP TO ROLE RAMEN_SVC_ROLE;
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA AUDIT TO ROLE RAMEN_SVC_ROLE;
GRANT USAGE ON ALL PROCEDURES IN SCHEMA APP TO ROLE RAMEN_SVC_ROLE;
GRANT USAGE ON WAREHOUSE RAMEN_APP_${ENV}_WH TO ROLE RAMEN_SVC_ROLE;

-- サービスアカウントにロールを付与（ユーザー作成後）:
-- GRANT ROLE RAMEN_SVC_ROLE TO USER ${SNOWFLAKE_SVC_USER};
