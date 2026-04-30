import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Alert,
  Box,
  Typography,
  Paper,
  Checkbox,
  FormControlLabel,
  Button,
} from "@mui/material";
import { postConsent } from "@/services/api";

interface Props {
  policyVersion: string;
}

export default function ConsentPage({ policyVersion }: Props) {
  const [agreed, setAgreed] = useState(false);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () => postConsent(policyVersion),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["auth", "consent"] });
    },
  });

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="80vh"
      p={2}
    >
      <Paper sx={{ maxWidth: 800, p: 4 }}>
        <Typography variant="h5" gutterBottom>
          プライバシーポリシー（v{policyVersion}）
        </Typography>

        <Box
          sx={{
            maxHeight: 400,
            overflow: "auto",
            border: 1,
            borderColor: "divider",
            borderRadius: 1,
            p: 2,
            mb: 3,
          }}
        >
          <Typography variant="body2" component="div">
            <h3>1. 利用目的</h3>
            <p>
              本システムは、ラーメンチェーン店舗の食材在庫管理・発注管理・配送管理を目的としています。
              取得した個人情報は、業務遂行に必要な範囲でのみ利用いたします。
            </p>
            <h3>2. 取得する情報</h3>
            <p>氏名、メールアドレス、所属店舗、ロール情報、操作履歴</p>
            <h3>3. 保存期間</h3>
            <ul>
              <li>匿名化データ: 3年</li>
              <li>商用データ: 10年</li>
              <li>監査ログ: 5年</li>
            </ul>
            <h3>4. 安全管理措置</h3>
            <p>
              ロールベースアクセス制御（RBAC）、通信暗号化（TLS）、
              データ暗号化（AES-256）を実施しています。
            </p>
            <h3>5. 同意の撤回</h3>
            <p>同意はいつでも撤回可能です。管理者にお問い合わせください。</p>
          </Typography>
        </Box>

        <FormControlLabel
          control={
            <Checkbox
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              data-testid="consent-checkbox"
            />
          }
          label="上記プライバシーポリシーに同意します"
        />

        {mutation.isError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            同意の送信に失敗しました。再度お試しください。
          </Alert>
        )}

        <Box mt={2}>
          <Button
            variant="contained"
            fullWidth
            disabled={!agreed || mutation.isPending}
            onClick={() => mutation.mutate()}
            data-testid="consent-submit"
          >
            {mutation.isPending ? "送信中..." : "同意して続行"}
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}
