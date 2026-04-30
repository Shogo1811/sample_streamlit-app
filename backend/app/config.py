"""アプリケーション設定（環境変数ベース）"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Azure AD
    azure_ad_tenant_id: str = ""
    azure_ad_client_id: str = ""
    azure_ad_manager_group_id: str = ""
    azure_ad_driver_group_id: str = ""

    # Snowflake
    snowflake_account: str = ""
    snowflake_user: str = ""
    snowflake_password: str = ""
    snowflake_private_key_path: str = ""
    snowflake_database: str = ""
    snowflake_schema: str = "APP"
    snowflake_warehouse: str = ""

    # App
    cors_origins: list[str] = ["http://localhost:5173"]
    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
