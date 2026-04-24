-- PROD環境パラメータ
-- 使用方法: source sql/setup_prod.sh && envsubst < sql/setup.sql | snowsql -f -
-- または: export ENV=PROD AUTO_SUSPEND_SEC=180 TIME_TRAVEL_DAYS=7 CREDIT_QUOTA=50
--         envsubst < sql/setup.sql | snowsql -f -

-- シェルスクリプト形式（.sh拡張子にリネームして使用可能）:
-- export ENV=PROD
-- export AUTO_SUSPEND_SEC=180
-- export TIME_TRAVEL_DAYS=7
-- export CREDIT_QUOTA=50
