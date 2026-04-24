"""プライバシーポリシー同意画面テスト"""

from unittest.mock import MagicMock, patch


class TestShowConsentPage:
    @patch("src.pages.privacy_consent.record_consent")
    @patch("src.pages.privacy_consent.st")
    def test_consent_granted(self, mock_st, mock_record):
        from src.pages.privacy_consent import show_consent_page

        mock_st.checkbox.return_value = True
        mock_st.button.return_value = True

        show_consent_page(MagicMock(), "TANAKA")
        mock_record.assert_called_once()
        mock_st.success.assert_called_once()

    @patch("src.pages.privacy_consent.st")
    def test_not_agreed(self, mock_st):
        from src.pages.privacy_consent import show_consent_page

        mock_st.checkbox.return_value = False
        mock_st.button.return_value = False

        show_consent_page(MagicMock(), "TANAKA")
        mock_st.info.assert_called_once()

    @patch("src.pages.privacy_consent.st")
    def test_agreed_not_submitted(self, mock_st):
        from src.pages.privacy_consent import show_consent_page

        mock_st.checkbox.return_value = True
        mock_st.button.return_value = False

        show_consent_page(MagicMock(), "TANAKA")
