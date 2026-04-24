-- 初期データ投入（DEV環境用）
-- 使用方法: envsubst < seed.sql | snowsql -f - (ENV=DEV をexportしてから実行)

USE ROLE SYSADMIN;
USE DATABASE RAMEN_LOGISTICS_${ENV}_DB;
USE SCHEMA APP;

-- 食材マスタ
INSERT INTO INGREDIENTS (ingredient_name, category, unit, threshold) VALUES
    ('中太麺', '麺類', 'kg', 20),
    ('細麺', '麺類', 'kg', 15),
    ('チャーシュー', 'トッピング', 'kg', 10),
    ('メンマ', 'トッピング', 'kg', 5),
    ('ネギ', 'トッピング', 'kg', 3),
    ('煮卵', 'トッピング', '個', 50),
    ('豚骨スープ', 'スープ', 'L', 30),
    ('味噌スープ', 'スープ', 'L', 20),
    ('醤油タレ', 'スープ', 'L', 10),
    ('海苔', 'トッピング', '枚', 100),
    ('にんにく', '薬味', 'kg', 2),
    ('生姜', '薬味', 'kg', 2);

-- テスト用店舗（manager_user_idはSnowflakeユーザー名）
INSERT INTO STORES (store_name, address, manager_user_id) VALUES
    ('ラーメン太郎 新宿店', '東京都新宿区西新宿1-1-1', 'TANAKA'),
    ('ラーメン太郎 渋谷店', '東京都渋谷区道玄坂1-1-1', 'YAMADA'),
    ('ラーメン太郎 池袋店', '東京都豊島区南池袋1-1-1', 'TANAKA');

-- テスト用ドライバー（snowflake_usernameはSnowflakeユーザー名 — RAP照合に使用）
INSERT INTO DRIVERS (driver_name, snowflake_username) VALUES
    ('佐藤一郎', 'SATO'),
    ('鈴木二郎', 'SUZUKI');

-- テスト用ユーザーロールマッピング
INSERT INTO USER_ROLE_MAPPING (user_id, role_type, related_id) VALUES
    ('TANAKA', 'MANAGER', 1),
    ('YAMADA', 'MANAGER', 2),
    ('SATO', 'DRIVER', 1),
    ('SUZUKI', 'DRIVER', 2);
