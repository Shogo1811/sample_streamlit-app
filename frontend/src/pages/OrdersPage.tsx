import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Snackbar,
} from "@mui/material";
import {
  fetchProposals,
  fetchOrderPlans,
  approveProposal,
  rejectProposal,
} from "@/services/api";
import ConfirmDialog from "@/components/ConfirmDialog";

const STATUS_COLORS: Record<string, "default" | "warning" | "success" | "error"> = {
  "生成": "default",
  "確認中": "warning",
  "承認": "success",
  "却下": "error",
};

export default function OrdersPage() {
  const [tab, setTab] = useState(0);
  const [approveTarget, setApproveTarget] = useState<{
    id: number;
    name: string;
    qty: number;
  } | null>(null);
  const [rejectTarget, setRejectTarget] = useState<{
    id: number;
    name: string;
  } | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({
    open: false,
    message: "",
    severity: "success",
  });
  const queryClient = useQueryClient();

  const { data: proposals, isLoading } = useQuery({
    queryKey: ["proposals", "確認中"],
    queryFn: () => fetchProposals("確認中"),
  });

  const { data: plans } = useQuery({
    queryKey: ["order-plans"],
    queryFn: fetchOrderPlans,
  });

  const approveMutation = useMutation({
    mutationFn: ({ id, qty }: { id: number; qty: number }) =>
      approveProposal(id, qty),
    onSuccess: (result) => {
      setApproveTarget(null);
            if (result.success) {
        setSnackbar({ open: true, message: result.message, severity: "success" });
        queryClient.invalidateQueries({ queryKey: ["proposals"] });
        queryClient.invalidateQueries({ queryKey: ["order-plans"] });
      } else {
        setSnackbar({ open: true, message: result.message, severity: "error" });
      }
    },
    onError: () => {
      setApproveTarget(null);
            setSnackbar({ open: true, message: "通信エラーが発生しました", severity: "error" });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (id: number) => rejectProposal(id),
    onSuccess: (result) => {
      setRejectTarget(null);
      if (result.success) {
        setSnackbar({ open: true, message: result.message, severity: "success" });
        queryClient.invalidateQueries({ queryKey: ["proposals"] });
      } else {
        setSnackbar({ open: true, message: result.message, severity: "error" });
      }
    },
    onError: () => {
      setRejectTarget(null);
      setSnackbar({ open: true, message: "通信エラーが発生しました", severity: "error" });
    },
  });

  const handleApproveConfirm = () => {
    if (!approveTarget) return;
    const qty = approveTarget.qty;
    approveMutation.mutate({ id: approveTarget.id, qty });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        発注提案管理
      </Typography>

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="発注提案リスト" />
        <Tab label="承認済み発注予定" />
      </Tabs>

      {tab === 0 && (
        <>
          {isLoading ? (
            <CircularProgress />
          ) : !proposals?.length ? (
            <Alert severity="info">確認中の発注提案はありません</Alert>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>食材</TableCell>
                    <TableCell>カテゴリ</TableCell>
                    <TableCell>推奨数量</TableCell>
                    <TableCell>理由</TableCell>
                    <TableCell>ステータス</TableCell>
                    <TableCell>操作</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {proposals.map((p) => (
                    <TableRow key={p.proposal_id}>
                      <TableCell>{p.ingredient_name}</TableCell>
                      <TableCell>{p.category}</TableCell>
                      <TableCell>{p.recommended_quantity}</TableCell>
                      <TableCell>{p.reason}</TableCell>
                      <TableCell>
                        <Chip
                          label={p.status}
                          color={STATUS_COLORS[p.status] || "default"}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="contained"
                          size="small"
                          color="success"
                          sx={{ mr: 1 }}
                          onClick={() =>
                            setApproveTarget({
                              id: p.proposal_id,
                              name: p.ingredient_name,
                              qty: p.recommended_quantity,
                            })
                          }
                          data-testid={`approve-${p.proposal_id}`}
                        >
                          承認
                        </Button>
                        <Button
                          variant="outlined"
                          size="small"
                          color="error"
                          onClick={() =>
                            setRejectTarget({
                              id: p.proposal_id,
                              name: p.ingredient_name,
                            })
                          }
                          data-testid={`reject-${p.proposal_id}`}
                        >
                          却下
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </>
      )}

      {tab === 1 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>食材</TableCell>
                <TableCell>数量</TableCell>
                <TableCell>承認者</TableCell>
                <TableCell>承認日時</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {plans?.map((p) => (
                <TableRow key={p.plan_id}>
                  <TableCell>{p.ingredient_name}</TableCell>
                  <TableCell>{p.quantity}</TableCell>
                  <TableCell>{p.approved_by}</TableCell>
                  <TableCell>
                    {new Date(p.approved_at).toLocaleString("ja-JP")}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* 承認ダイアログ */}
      <ConfirmDialog
        open={!!approveTarget}
        title="発注提案の承認"
        message={`「${approveTarget?.name}」を承認しますか？`}
        onConfirm={handleApproveConfirm}
        onCancel={() => {
          setApproveTarget(null);
                  }}
        confirmLabel="承認する"
        loading={approveMutation.isPending}
      />
      {/* 却下ダイアログ */}
      <ConfirmDialog
        open={!!rejectTarget}
        title="発注提案の却下"
        message={`「${rejectTarget?.name}」を却下しますか？`}
        onConfirm={() => rejectTarget && rejectMutation.mutate(rejectTarget.id)}
        onCancel={() => setRejectTarget(null)}
        confirmLabel="却下する"
        loading={rejectMutation.isPending}
      />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar((s) => ({ ...s, open: false }))}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar((s) => ({ ...s, open: false }))}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

