-- ============================================================
-- ラーメンチェーン食材自動発注システム - Snowflakeインフラ設定
-- 実行前提: ACCOUNTADMINロールで実行すること
-- 環境変数: ${ENV} = DEV / STG / PROD
-- ============================================================

-- ------------------------------------------------------------
-- 1. データベース・スキーマ
-- ------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS RAMEN_LOGISTICS_${ENV}_DB;
USE DATABASE RAMEN_LOGISTICS_${ENV}_DB;
CREATE SCHEMA IF NOT EXISTS APP;
CREATE SCHEMA IF NOT EXISTS AUDIT;

-- SiSデプロイ用ステージ
CREATE STAGE IF NOT EXISTS APP.STREAMLIT_STAGE;
USE SCHEMA APP;

-- ------------------------------------------------------------
-- 2. Warehouse
-- ------------------------------------------------------------
CREATE WAREHOUSE IF NOT EXISTS RAMEN_APP_${ENV}_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = ${AUTO_SUSPEND_SEC}  -- DEV:60, PROD:180
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 1;

CREATE WAREHOUSE IF NOT EXISTS RAMEN_TASK_${ENV}_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

-- ------------------------------------------------------------
-- 3. ロール
-- ------------------------------------------------------------
CREATE ROLE IF NOT EXISTS APP_ADMIN_ROLE;
CREATE ROLE IF NOT EXISTS MANAGER_ROLE;
CREATE ROLE IF NOT EXISTS DRIVER_ROLE;

-- ロール階層
GRANT ROLE MANAGER_ROLE TO ROLE APP_ADMIN_ROLE;
GRANT ROLE DRIVER_ROLE TO ROLE APP_ADMIN_ROLE;
GRANT ROLE APP_ADMIN_ROLE TO ROLE SYSADMIN;

-- Warehouse使用権限
GRANT USAGE ON WAREHOUSE RAMEN_APP_${ENV}_WH TO ROLE APP_ADMIN_ROLE;
GRANT USAGE ON WAREHOUSE RAMEN_TASK_${ENV}_WH TO ROLE SYSADMIN;
GRANT USAGE ON DATABASE RAMEN_LOGISTICS_${ENV}_DB TO ROLE APP_ADMIN_ROLE;
GRANT USAGE ON SCHEMA APP TO ROLE APP_ADMIN_ROLE;
GRANT USAGE ON SCHEMA AUDIT TO ROLE APP_ADMIN_ROLE;

-- Task実行権限
GRANT EXECUTE TASK ON ACCOUNT TO ROLE SYSADMIN;

-- ------------------------------------------------------------
-- 4. テーブル（CHECK制約付き）
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS APP.STORES (
    store_id INT AUTOINCREMENT PRIMARY KEY,
    store_name VARCHAR(200) NOT NULL,
    address VARCHAR(500),
    manager_user_id VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS APP.INGREDIENTS (
    ingredient_id INT AUTOINCREMENT PRIMARY KEY,
    ingredient_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    threshold INT NOT NULL DEFAULT 10 CHECK (threshold >= 0)
);

CREATE TABLE IF NOT EXISTS APP.INVENTORY (
    store_id INT NOT NULL REFERENCES APP.STORES(store_id),
    ingredient_id INT NOT NULL REFERENCES APP.INGREDIENTS(ingredient_id),
    current_quantity INT NOT NULL DEFAULT 0 CHECK (current_quantity >= 0),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (store_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS APP.ORDER_PROPOSALS (
    proposal_id INT AUTOINCREMENT PRIMARY KEY,
    store_id INT NOT NULL REFERENCES APP.STORES(store_id),
    ingredient_id INT NOT NULL REFERENCES APP.INGREDIENTS(ingredient_id),
    recommended_quantity INT NOT NULL CHECK (recommended_quantity >= 1),
    reason VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT '生成' CHECK (status IN ('生成', '確認中', '承認', '却下')),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS APP.ORDER_PLANS (
    plan_id INT AUTOINCREMENT PRIMARY KEY,
    proposal_id INT NOT NULL REFERENCES APP.ORDER_PROPOSALS(proposal_id),
    store_id INT NOT NULL REFERENCES APP.STORES(store_id),  -- 非正規化（RAP適用用）
    approved_by VARCHAR(100) NOT NULL,
    approved_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    quantity INT NOT NULL CHECK (quantity >= 1 AND quantity <= 10000)
);

CREATE TABLE IF NOT EXISTS APP.DRIVERS (
    driver_id INT AUTOINCREMENT PRIMARY KEY,
    driver_name VARCHAR(200) NOT NULL,
    snowflake_username VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS APP.DELIVERIES (
    delivery_id INT AUTOINCREMENT PRIMARY KEY,
    driver_id INT NOT NULL REFERENCES APP.DRIVERS(driver_id),
    store_id INT NOT NULL REFERENCES APP.STORES(store_id),
    status VARCHAR(20) NOT NULL DEFAULT '未配送' CHECK (status IN ('未配送', '配送中', '配送完了')),
    scheduled_at TIMESTAMP_NTZ,
    completed_at TIMESTAMP_NTZ
);

CREATE TABLE IF NOT EXISTS APP.USER_ROLE_MAPPING (
    user_id VARCHAR(100) NOT NULL,
    role_type VARCHAR(20) NOT NULL CHECK (role_type IN ('MANAGER', 'DRIVER')),
    related_id INT NOT NULL,
    PRIMARY KEY (user_id, role_type)  -- 複合キー: 1ユーザーが複数ロール可能
);

-- 同意記録（AUDIT スキーマ — 法的証跡として保護）
CREATE TABLE IF NOT EXISTS AUDIT.CONSENT_RECORDS (
    record_id INT AUTOINCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    consent_type VARCHAR(20) NOT NULL DEFAULT 'GRANT' CHECK (consent_type IN ('GRANT', 'REVOKE')),
    consented_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    policy_version VARCHAR(20) NOT NULL,
    revocation_reason VARCHAR(500)
);

-- 監査ログ（APPEND-ONLY）
CREATE TABLE IF NOT EXISTS AUDIT.AUDIT_LOG (
    log_id INT AUTOINCREMENT PRIMARY KEY,
    operator VARCHAR(100) NOT NULL,
    operated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    operation_type VARCHAR(50) NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    target_record_id INT,
    before_value VARIANT,
    after_value VARIANT
);

-- ------------------------------------------------------------
-- 5. テーブルオーナーシップ・権限
-- ------------------------------------------------------------

-- 監査ログ: SYSADMINオーナー（APPEND-ONLY保証）
GRANT OWNERSHIP ON TABLE AUDIT.AUDIT_LOG TO ROLE SYSADMIN COPY CURRENT GRANTS;
GRANT OWNERSHIP ON TABLE AUDIT.CONSENT_RECORDS TO ROLE SYSADMIN COPY CURRENT GRANTS;

-- APP_ADMIN_ROLE: SELECT（APPスキーマ全テーブル）
GRANT SELECT ON ALL TABLES IN SCHEMA APP TO ROLE APP_ADMIN_ROLE;
GRANT SELECT ON FUTURE TABLES IN SCHEMA APP TO ROLE APP_ADMIN_ROLE;

-- 監査系: INSERT ONLY（APPEND-ONLY保証）
GRANT INSERT ON TABLE AUDIT.AUDIT_LOG TO ROLE APP_ADMIN_ROLE;
GRANT INSERT ON TABLE AUDIT.CONSENT_RECORDS TO ROLE APP_ADMIN_ROLE;
GRANT SELECT ON TABLE AUDIT.CONSENT_RECORDS TO ROLE APP_ADMIN_ROLE;
-- UPDATE/DELETEは一切GRANTしない

-- ユーザーロールマッピング: SECURITYADMINが管理
GRANT OWNERSHIP ON TABLE APP.USER_ROLE_MAPPING TO ROLE SECURITYADMIN COPY CURRENT GRANTS;
GRANT SELECT ON TABLE APP.USER_ROLE_MAPPING TO ROLE APP_ADMIN_ROLE;

-- SP実行権限（FUTURE: Part 2でSP作成後に自動適用される）
GRANT USAGE ON FUTURE PROCEDURES IN SCHEMA APP TO ROLE APP_ADMIN_ROLE;

-- ------------------------------------------------------------
-- 6. Row Access Policy（カラム名衝突修正済み）
-- ------------------------------------------------------------

-- 店舗ベースRAP（在庫、発注提案、発注予定に適用）
CREATE OR REPLACE ROW ACCESS POLICY APP.STORE_RAP AS (policy_store_id INT)
RETURNS BOOLEAN ->
    -- 店長: 自店舗のみ
    policy_store_id IN (
        SELECT related_id
        FROM APP.USER_ROLE_MAPPING
        WHERE user_id = CURRENT_USER()
          AND role_type = 'MANAGER'
    )
    OR
    -- ドライバー: 自分が配送担当の店舗のみ
    EXISTS (
        SELECT 1 FROM APP.USER_ROLE_MAPPING urm
        JOIN APP.DELIVERIES d ON d.driver_id = urm.related_id
        WHERE urm.user_id = CURRENT_USER()
          AND urm.role_type = 'DRIVER'
          AND d.store_id = policy_store_id
    );

-- ドライバーベースRAP（配送テーブルに適用）
CREATE OR REPLACE ROW ACCESS POLICY APP.DELIVERY_RAP AS (policy_driver_id INT, policy_store_id INT)
RETURNS BOOLEAN ->
    (policy_driver_id IN (
        SELECT related_id
        FROM APP.USER_ROLE_MAPPING
        WHERE user_id = CURRENT_USER()
          AND role_type = 'DRIVER'
    ))
    OR
    (policy_store_id IN (
        SELECT related_id
        FROM APP.USER_ROLE_MAPPING
        WHERE user_id = CURRENT_USER()
          AND role_type = 'MANAGER'
    ));

-- 同意記録RAP（自分のレコードのみ閲覧可能）
CREATE OR REPLACE ROW ACCESS POLICY AUDIT.CONSENT_RAP AS (policy_user_id VARCHAR)
RETURNS BOOLEAN ->
    policy_user_id = CURRENT_USER();

-- RAP適用
ALTER TABLE APP.INVENTORY ADD ROW ACCESS POLICY APP.STORE_RAP ON (store_id);
ALTER TABLE APP.ORDER_PROPOSALS ADD ROW ACCESS POLICY APP.STORE_RAP ON (store_id);
ALTER TABLE APP.ORDER_PLANS ADD ROW ACCESS POLICY APP.STORE_RAP ON (store_id);
ALTER TABLE APP.DELIVERIES ADD ROW ACCESS POLICY APP.DELIVERY_RAP ON (driver_id, store_id);
ALTER TABLE AUDIT.CONSENT_RECORDS ADD ROW ACCESS POLICY AUDIT.CONSENT_RAP ON (user_id);

-- ------------------------------------------------------------
-- 7. Stored Procedures（OWNER'S RIGHTS — ビジネスロジック実装済み）
-- 共通ルール:
--   - EXECUTE AS OWNER: SP内のSQL文はオーナーロール（SYSADMIN）で実行
--   - CURRENT_USER() + USER_ROLE_MAPPING照合で操作権限を検証
--   - 不正な状態遷移はエラーメッセージを返却
--   - 全操作は監査ログ（AUDIT.AUDIT_LOG）へのINSERTを含む
-- ------------------------------------------------------------

-- === SP_APPROVE_ORDER_PROPOSAL ===
-- 発注提案の承認処理（アトミック: 遷移バリデーション→数量検証→ORDER_PLANS作成→監査ログ）
CREATE OR REPLACE PROCEDURE APP.SP_APPROVE_ORDER_PROPOSAL(
    p_proposal_id INT, p_quantity INT, p_user_id VARCHAR
)
RETURNS VARIANT
LANGUAGE SQL
EXECUTE AS OWNER
AS
$$
DECLARE
    v_role_count INT DEFAULT 0;
    v_current_status VARCHAR DEFAULT NULL;
    v_store_id INT DEFAULT NULL;
BEGIN
    -- 1. ユーザーロール検証（MANAGERロール必須）
    SELECT COUNT(*) INTO v_role_count
    FROM APP.USER_ROLE_MAPPING
    WHERE user_id = :p_user_id AND role_type = 'MANAGER';

    IF (v_role_count = 0) THEN
        RETURN OBJECT_CONSTRUCT('success', FALSE, 'message', '権限がありません: MANAGERロールが必要です');
    END IF;

    -- 2. 提案存在確認 + ステータス・店舗ID取得
    SELECT status, store_id INTO v_current_status, v_store_id
    FROM APP.ORDER_PROPOSALS
    WHERE proposal_id = :p_proposal_id;

    IF (v_current_status IS NULL) THEN
        RETURN OBJECT_CONSTRUCT('success', FALSE, 'message', '指定された提案が見つかりません');
    END IF;

    -- 3. 状態遷移バリデーション（確認中→承認のみ許可）
    IF (v_current_status != '確認中') THEN
        RETURN OBJECT_CONSTRUCT('success', FALSE, 'message',
            'ステータスを「' || v_current_status || '」から「承認」に変更することはできません');
    END IF;

    -- 4. 数量バリデーション（NFR-09: 1〜10,000整数）
    IF (:p_quantity < 1 OR :p_quantity > 10000) THEN
        RETURN OBJECT_CONSTRUCT('success', FALSE, 'message', '発注数量は1以上10,000以下で入力してください');
    END IF;

    -- 5. ステータス更新（確認中→承認）
    UPDATE APP.ORDER_PROPOSALS
    SET status = '承認'
    WHERE proposal_id = :p_proposal_id AND status = '確認中';

    -- 6. 発注予定レコード作成
    INSERT INTO APP.ORDER_PLANS (proposal_id, store_id, approved_by, quantity)
    VALUES (:p_proposal_id, :v_store_id, :p_user_id, :p_quantity);

    -- 7. 監査ログ記録
    INSERT INTO AUDIT.AUDIT_LOG (operator, operation_type, target_table, target_record_id, after_value)
    VALUES (:p_user_id, 'APPROVE_PROPOSAL', 'ORDER_PROPOSALS', :p_proposal_id,
            OBJECT_CONSTRUCT('quantity', :p_quantity, 'status', '承認', 'store_id', :v_store_id));

    RETURN OBJECT_CONSTRUCT('success', TRUE, 'message', '承認しました');
END;
$$;

-- === SP_REJECT_ORDER_PROPOSAL ===
-- 発注提案の却下処理（遷移バリデーション→ステータス更新→監査ログ）
CREATE OR REPLACE PROCEDURE APP.SP_REJECT_ORDER_PROPOSAL(
    p_proposal_id INT, p_user_id VARCHAR
)
RETURNS VARIANT
LANGUAGE SQL
EXECUTE AS OWNER
AS
$$
DECLARE
    v_role_count INT DEFAULT 0;
    v_current_status VARCHAR DEFAULT NULL;
BEGIN
    -- 1. ユーザーロール検証
    SELECT COUNT(*) INTO v_role_count
    FROM APP.USER_ROLE_MAPPING
    WHERE user_id = :p_user_id AND role_type = 'MANAGER';

    IF (v_role_count = 0) THEN
        RETURN OBJECT_CONSTRUCT('success', FALSE, 'message', '権限がありません: MANAGERロールが必要です');
    END IF;

    -- 2. 提案存在確認 + ステータス取得
    SELECT status INTO v_current_status
    FROM APP.ORDER_PROPOSALS
    WHERE proposal_id = :p_proposal_id;

    IF (v_current_status IS NULL) THEN
        RETURN OBJECT_CONSTRUCT('success', FALSE, 'message', '指定された提案が見つかりません');
    END IF;

    -- 3. 状態遷移バリデーション（確認中→却下のみ許可）
    IF (v_current_status != '確認中') THEN
        RETURN OBJECT_CONSTRUCT('success', FALSE, 'message',
            'ステータスを「' || v_current_status || '」から「却下」に変更することはできません');
    END IF;

    -- 4. ステータス更新
    UPDATE APP.ORDER_PROPOSALS
    SET status = '却下'
    WHERE proposal_id = :p_proposal_id AND status = '確認中';

    -- 5. 監査ログ記録
    INSERT INTO AUDIT.AUDIT_LOG (operator, operation_type, target_table, target_record_id, after_value)
    VALUES (:p_user_id, 'REJECT_PROPOSAL', 'ORDER_PROPOSALS', :p_proposal_id,
            OBJECT_CONSTRUCT('status', '却下'));

    RETURN OBJECT_CONSTRUCT('success', TRUE, 'message', '却下しました');
END;
$$;

-- === SP_COMPLETE_DELIVERY ===
-- 配送完了報告（遷移バリデーション→ステータス更新→完了日時記録→監査ログ）
CREATE OR REPLACE PROCEDURE APP.SP_COMPLETE_DELIVERY(
    p_delivery_id INT, p_user_id VARCHAR
)
RETURNS VARIANT
LANGUAGE SQL
EXECUTE AS OWNER
AS
$$
DECLARE
    v_role_count INT DEFAULT 0;
    v_current_status VARCHAR DEFAULT NULL;
    v_store_id INT DEFAULT NULL;
BEGIN
    -- 1. ユーザーロール検証（DRIVERロール必須）
    SELECT COUNT(*) INTO v_role_count
    FROM APP.USER_ROLE_MAPPING
    WHERE user_id = :p_user_id AND role_type = 'DRIVER';

    IF (v_role_count = 0) THEN
        RETURN OBJECT_CONSTRUCT('success', FALSE, 'message', '権限がありません: DRIVERロールが必要です');
    END IF;

    -- 2. 配送存在確認 + ステータス取得
    SELECT status, store_id INTO v_current_status, v_store_id
    FROM APP.DELIVERIES
    WHERE delivery_id = :p_delivery_id;

    IF (v_current_status IS NULL) THEN
        RETURN OBJECT_CONSTRUCT('success', FALSE, 'message', '指定された配送が見つかりません');
    END IF;

    -- 3. 状態遷移バリデーション（配送中→配送完了のみ許可）
    IF (v_current_status != '配送中') THEN
        RETURN OBJECT_CONSTRUCT('success', FALSE, 'message',
            'ステータスを「' || v_current_status || '」から「配送完了」に変更することはできません');
    END IF;

    -- 4. ステータス更新 + 完了日時記録
    UPDATE APP.DELIVERIES
    SET status = '配送完了', completed_at = CURRENT_TIMESTAMP()
    WHERE delivery_id = :p_delivery_id AND status = '配送中';

    -- 5. 監査ログ記録
    INSERT INTO AUDIT.AUDIT_LOG (operator, operation_type, target_table, target_record_id, after_value)
    VALUES (:p_user_id, 'COMPLETE_DELIVERY', 'DELIVERIES', :p_delivery_id,
            OBJECT_CONSTRUCT('status', '配送完了', 'store_id', :v_store_id));

    RETURN OBJECT_CONSTRUCT('success', TRUE, 'message', '配送完了を報告しました');
END;
$$;

-- === SP_GENERATE_ORDER_PROPOSALS ===
-- 発注提案の自動生成（Snowflake Tasks経由で定期実行）
-- ロジック: 在庫が閾値以下の食材に対して、(閾値×2 - 現在庫) の推奨発注数で提案を生成
CREATE OR REPLACE PROCEDURE APP.SP_GENERATE_ORDER_PROPOSALS()
RETURNS INT
LANGUAGE SQL
EXECUTE AS OWNER
AS
$$
DECLARE
    v_count INT DEFAULT 0;
BEGIN
    -- 在庫が閾値以下かつ未処理の提案がない食材に対して発注提案を自動生成
    INSERT INTO APP.ORDER_PROPOSALS (store_id, ingredient_id, recommended_quantity, reason, status)
    SELECT
        inv.store_id,
        inv.ingredient_id,
        GREATEST(ing.threshold * 2 - inv.current_quantity, 1) AS recommended_quantity,
        '自動生成: 在庫(' || inv.current_quantity || ing.unit || ')が閾値(' || ing.threshold || ing.unit || ')以下' AS reason,
        '生成' AS status
    FROM APP.INVENTORY inv
    JOIN APP.INGREDIENTS ing ON inv.ingredient_id = ing.ingredient_id
    WHERE inv.current_quantity <= ing.threshold
      AND NOT EXISTS (
          SELECT 1 FROM APP.ORDER_PROPOSALS op
          WHERE op.store_id = inv.store_id
            AND op.ingredient_id = inv.ingredient_id
            AND op.status IN ('生成', '確認中')
      );

    SELECT COUNT(*) INTO v_count
    FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));

    -- 生成した提案の件数を監査ログに記録
    IF (v_count > 0) THEN
        INSERT INTO AUDIT.AUDIT_LOG (operator, operation_type, target_table, target_record_id, after_value)
        VALUES ('SYSTEM', 'GENERATE_PROPOSALS', 'ORDER_PROPOSALS', NULL,
                OBJECT_CONSTRUCT('generated_count', :v_count));
    END IF;

    RETURN v_count;
END;
$$;

-- === SP_UPDATE_DELIVERY_STATUS_BATCH ===
-- 配送ステータス一括更新（未配送→配送中: 予定時刻到達分）
-- Snowflake Tasks経由で定期実行
CREATE OR REPLACE PROCEDURE APP.SP_UPDATE_DELIVERY_STATUS_BATCH()
RETURNS INT
LANGUAGE SQL
EXECUTE AS OWNER
AS
$$
DECLARE
    v_count INT DEFAULT 0;
BEGIN
    -- 予定時刻を過ぎた未配送の配送を配送中に更新
    UPDATE APP.DELIVERIES
    SET status = '配送中'
    WHERE status = '未配送'
      AND scheduled_at <= CURRENT_TIMESTAMP();

    -- 更新件数を取得
    v_count := SQLROWCOUNT;

    IF (v_count > 0) THEN
        INSERT INTO AUDIT.AUDIT_LOG (operator, operation_type, target_table, target_record_id, after_value)
        VALUES ('SYSTEM', 'BATCH_STATUS_UPDATE', 'DELIVERIES', NULL,
                OBJECT_CONSTRUCT('updated_count', :v_count, 'transition', '未配送→配送中'));
    END IF;

    RETURN v_count;
END;
$$;

-- === SP_CLEANUP_EXPIRED_DATA ===
-- NFR-16: データ保持期間管理
-- 個人情報: 3年超で匿名化（driver_name, snowflake_username）
-- 監査ログ: 5年超で削除
-- 取引記録（数量等）: 商法第19条に基づき10年間保持
CREATE OR REPLACE PROCEDURE APP.SP_CLEANUP_EXPIRED_DATA()
RETURNS INT
LANGUAGE SQL
EXECUTE AS OWNER
AS
$$
DECLARE
    v_total INT DEFAULT 0;
    v_anonymized INT DEFAULT 0;
    v_deleted_logs INT DEFAULT 0;
BEGIN
    -- 1. 配送履歴の個人情報匿名化（3年超）
    --    driver_nameを匿名化し、対応するUSER_ROLE_MAPPINGも無効化
    UPDATE APP.DRIVERS d
    SET driver_name = 'ANONYMIZED_' || d.driver_id::VARCHAR,
        snowflake_username = 'ANONYMIZED_' || d.driver_id::VARCHAR
    WHERE d.driver_name NOT LIKE 'ANONYMIZED_%'
      AND NOT EXISTS (
          SELECT 1 FROM APP.DELIVERIES del
          WHERE del.driver_id = d.driver_id
            AND del.scheduled_at > DATEADD(YEAR, -3, CURRENT_TIMESTAMP())
      )
      AND NOT EXISTS (
          SELECT 1 FROM APP.DELIVERIES del
          WHERE del.driver_id = d.driver_id
            AND del.status IN ('未配送', '配送中')
      );

    v_anonymized := SQLROWCOUNT;

    -- 2. 同意記録の個人情報匿名化（3年超・撤回済みのみ）
    UPDATE AUDIT.CONSENT_RECORDS
    SET user_id = 'ANONYMIZED_' || record_id::VARCHAR
    WHERE user_id NOT LIKE 'ANONYMIZED_%'
      AND consented_at < DATEADD(YEAR, -3, CURRENT_TIMESTAMP())
      AND consent_type = 'REVOKE';

    v_anonymized := v_anonymized + SQLROWCOUNT;

    -- 3. 監査ログの削除（5年超）
    DELETE FROM AUDIT.AUDIT_LOG
    WHERE operated_at < DATEADD(YEAR, -5, CURRENT_TIMESTAMP());

    v_deleted_logs := SQLROWCOUNT;

    v_total := v_anonymized + v_deleted_logs;

    IF (v_total > 0) THEN
        INSERT INTO AUDIT.AUDIT_LOG (operator, operation_type, target_table, target_record_id, after_value)
        VALUES ('SYSTEM', 'CLEANUP_EXPIRED_DATA', 'MULTIPLE', NULL,
                OBJECT_CONSTRUCT('anonymized', :v_anonymized, 'deleted_logs', :v_deleted_logs));
    END IF;

    RETURN v_total;
END;
$$;

-- ------------------------------------------------------------
-- 8. Time Travel（全業務テーブル）
-- ------------------------------------------------------------
ALTER TABLE APP.STORES SET DATA_RETENTION_TIME_IN_DAYS = ${TIME_TRAVEL_DAYS};
ALTER TABLE APP.INVENTORY SET DATA_RETENTION_TIME_IN_DAYS = ${TIME_TRAVEL_DAYS};
ALTER TABLE APP.ORDER_PROPOSALS SET DATA_RETENTION_TIME_IN_DAYS = ${TIME_TRAVEL_DAYS};
ALTER TABLE APP.ORDER_PLANS SET DATA_RETENTION_TIME_IN_DAYS = ${TIME_TRAVEL_DAYS};
ALTER TABLE APP.DELIVERIES SET DATA_RETENTION_TIME_IN_DAYS = ${TIME_TRAVEL_DAYS};
ALTER TABLE APP.DRIVERS SET DATA_RETENTION_TIME_IN_DAYS = ${TIME_TRAVEL_DAYS};

-- ------------------------------------------------------------
-- 9. Resource Monitor（ACCOUNTADMINロールが必要）
-- ------------------------------------------------------------
USE ROLE ACCOUNTADMIN;

CREATE OR REPLACE RESOURCE MONITOR RAMEN_${ENV}_MONITOR
    WITH CREDIT_QUOTA = ${CREDIT_QUOTA}  -- DEV:5, STG:10, PROD:50
    FREQUENCY = MONTHLY
    START_TIMESTAMP = IMMEDIATELY
    TRIGGERS
        ON 80 PERCENT DO NOTIFY
        ON 100 PERCENT DO SUSPEND;

ALTER WAREHOUSE RAMEN_APP_${ENV}_WH SET RESOURCE_MONITOR = RAMEN_${ENV}_MONITOR;
ALTER WAREHOUSE RAMEN_TASK_${ENV}_WH SET RESOURCE_MONITOR = RAMEN_${ENV}_MONITOR;

USE ROLE SYSADMIN;

-- ------------------------------------------------------------
-- 10. Snowflake Tasks（SP経由に統一 — 監査ログ記録を保証）
-- NOTE: TasksはPart 2でSP実装完了後にRESUMEすること
-- ------------------------------------------------------------

CREATE OR REPLACE TASK APP.TASK_GENERATE_PROPOSALS
    WAREHOUSE = RAMEN_TASK_${ENV}_WH
    SCHEDULE = 'USING CRON 0 21 * * * UTC'  -- 06:00 JST
    AS
    CALL APP.SP_GENERATE_ORDER_PROPOSALS();

CREATE OR REPLACE TASK APP.TASK_CLEANUP_DATA
    WAREHOUSE = RAMEN_TASK_${ENV}_WH
    SCHEDULE = 'USING CRON 0 18 1 * * UTC'  -- 03:00 JST 毎月1日
    AS
    CALL APP.SP_CLEANUP_EXPIRED_DATA();

-- 配送ステータス自動遷移（SP経由 — 監査ログ記録あり）
CREATE OR REPLACE TASK APP.TASK_UPDATE_DELIVERY_STATUS
    WAREHOUSE = RAMEN_TASK_${ENV}_WH
    SCHEDULE = 'USING CRON 0 20 * * * UTC'  -- 05:00 JST
    AS
    CALL APP.SP_UPDATE_DELIVERY_STATUS_BATCH();

-- NOTE: Part 2でSP実装完了後に以下を実行してTasksを有効化する
-- ALTER TASK APP.TASK_GENERATE_PROPOSALS RESUME;
-- ALTER TASK APP.TASK_CLEANUP_DATA RESUME;
-- ALTER TASK APP.TASK_UPDATE_DELIVERY_STATUS RESUME;
