-- DEV環境パラメータ
-- 使用方法: source sql/setup_dev.sh && envsubst < sql/setup.sql | snowsql -f -
-- または: export ENV=DEV AUTO_SUSPEND_SEC=60 TIME_TRAVEL_DAYS=1 CREDIT_QUOTA=5
--         envsubst < sql/setup.sql | snowsql -f -

-- シェルスクリプト形式（.sh拡張子にリネームして使用可能）:
-- export ENV=DEV
-- export AUTO_SUSPEND_SEC=60
-- export TIME_TRAVEL_DAYS=1
-- export CREDIT_QUOTA=5
