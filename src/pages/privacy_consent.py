"""プライバシーポリシー同意画面"""

import streamlit as st
from snowflake.snowpark import Session

from src.dal.auth import record_consent
from src.utils.constants import CURRENT_POLICY_VERSION

PRIVACY_POLICY_TEXT = f"""
## プライバシーポリシー

**制定日**: 2026年4月1日 | **最終改定日**: 2026年4月1日 | **バージョン**: {CURRENT_POLICY_VERSION}

### 1. 事業者情報
- **事業者名**: （運営会社名を記載してください）
- **代表者**: （代表者名を記載してください）
- **所在地**: （所在地を記載してください）
- **お問い合わせ窓口**: privacy@example.com

### 2. 利用目的
本システムでは、以下の目的で個人情報を取り扱います。
1. 配送業務の遂行および配送スケジュールの管理
2. 食材の在庫管理および発注業務の効率化
3. 配送実績の記録および業務改善分析
4. ログイン日時・操作内容のログをセキュリティ目的で記録・分析

### 3. 取り扱う個人情報
- ドライバー氏名、配送スケジュール
- 店長の操作履歴（発注承認・配送ステータス更新等）

### 4. データ保持期間
- 配送履歴・発注履歴の個人情報部分: 3年間保持後に匿名化
- 取引記録（数量等）: 商法第19条に基づき10年間保持
- 監査ログ: 5年間保持

### 5. 安全管理措置
- **組織的措置**: ロールベースアクセス制御（RBAC）、行レベルセキュリティ（RAP）、操作監査ログ
- **技術的措置**: Snowflake AES-256暗号化（保管時・転送時）、パラメータバインドによるSQLインジェクション防止
- **物理的措置**: 日本国内リージョン（AWS ap-northeast-1 Tokyo）でのデータ保管

### 6. 第三者提供について
原則として、本人の同意なく個人情報を第三者に提供しません。
ただし、以下の場合を除きます:
- 法令に基づく場合
- 業務委託先への提供（委託先に対しては適切な監督を行います）

### 7. 開示等請求の手続き
保有個人データの開示・訂正・削除・利用停止の請求は、以下の手順で行えます:
1. **受付窓口**: 上記お問い合わせ窓口にメールでご連絡ください
2. **本人確認**: 社員証等の本人確認書類をご提示いただきます
3. **手数料**: 無料
4. **応答期限**: 受付から2週間以内に回答いたします

### 8. 同意の撤回について
同意はいつでも撤回できます。撤回を希望される場合は上記窓口にご連絡ください。
- 申請受付後、2営業日以内にシステム機能を停止します
- 5営業日以内に個人情報を匿名化処理します
- 匿名化後のデータは統計目的でのみ利用します

### 9. Cookie・セッション管理
本システムはStreamlit in Snowflake (SiS) 環境で動作し、
Snowflakeのセッション管理機能を使用します。トラッキング目的のCookieは使用しません。

### 10. データ保管先
日本国内リージョン（AWS ap-northeast-1 Tokyo）
"""


def show_consent_page(session: Session, user_id: str) -> None:
    """同意画面を表示"""
    st.title("プライバシーポリシー")
    st.markdown(PRIVACY_POLICY_TEXT)

    agreed = st.checkbox("上記プライバシーポリシーに同意します", key="privacy_consent")

    if st.button("同意して利用を開始する", disabled=not agreed, use_container_width=True):
        record_consent(session, user_id, CURRENT_POLICY_VERSION)
        st.success("同意が記録されました。")
        st.rerun()

    if not agreed:
        st.info("同意いただかないとシステムをご利用いただけません。")
