import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  CircularProgress,
  Alert,
  Snackbar,
  Stack,
} from "@mui/material";
import { fetchMyDeliveries, completeDelivery } from "@/services/api";
import ConfirmDialog from "@/components/ConfirmDialog";

export default function DriverPage() {
  const [completeTarget, setCompleteTarget] = useState<{
    id: number;
    name: string;
  } | null>(null);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: "success" | "error";
  }>({
    open: false,
    message: "",
    severity: "success",
  });
  const queryClient = useQueryClient();

  const { data: deliveries, isLoading } = useQuery({
    queryKey: ["my-deliveries"],
    queryFn: fetchMyDeliveries,
  });

  const completeMutation = useMutation({
    mutationFn: (id: number) => completeDelivery(id),
    onSuccess: (result) => {
      setCompleteTarget(null);
      if (result.success) {
        setSnackbar({
          open: true,
          message: result.message,
          severity: "success",
        });
        queryClient.invalidateQueries({ queryKey: ["my-deliveries"] });
      } else {
        setSnackbar({ open: true, message: result.message, severity: "error" });
      }
    },
    onError: () => {
      setCompleteTarget(null);
      setSnackbar({ open: true, message: "通信エラーが発生しました", severity: "error" });
    },
  });

  const completed = deliveries?.filter((d) => d.status === "配送完了") ?? [];
  const remaining = deliveries?.filter((d) => d.status !== "配送完了") ?? [];

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 600, mx: "auto" }}>
      <Typography variant="h5" gutterBottom>
        本日の配送
      </Typography>

      <Alert severity="info" sx={{ mb: 2 }}>
        完了: {completed.length}件 / 残り: {remaining.length}件
      </Alert>

      <Stack spacing={2}>
        {deliveries?.map((d) => (
          <Card
            key={d.delivery_id}
            data-testid={`driver-card-${d.delivery_id}`}
            sx={{
              opacity: d.status === "配送完了" ? 0.6 : 1,
            }}
          >
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold">
                {d.store_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                予定: {new Date(d.scheduled_at).toLocaleString("ja-JP")}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ステータス: {d.status}
              </Typography>
            </CardContent>
            {d.status === "配送中" && (
              <CardActions>
                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  onClick={() =>
                    setCompleteTarget({
                      id: d.delivery_id,
                      name: d.store_name,
                    })
                  }
                  sx={{ minHeight: 48 }}
                  data-testid={`complete-${d.delivery_id}`}
                >
                  配送完了
                </Button>
              </CardActions>
            )}
          </Card>
        ))}
      </Stack>

      <ConfirmDialog
        open={!!completeTarget}
        title="配送完了の確認"
        message={`「${completeTarget?.name}」への配送を完了しますか？`}
        onConfirm={() =>
          completeTarget && completeMutation.mutate(completeTarget.id)
        }
        onCancel={() => setCompleteTarget(null)}
        confirmLabel="完了する"
        loading={completeMutation.isPending}
      />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar((s) => ({ ...s, open: false }))}
      >
        <Alert
          severity={snackbar.severity}
          onClose={() => setSnackbar((s) => ({ ...s, open: false }))}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
