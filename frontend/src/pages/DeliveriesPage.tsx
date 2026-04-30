import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Grid,
  Chip,
  CircularProgress,
  Alert,
} from "@mui/material";
import LocalShippingIcon from "@mui/icons-material/LocalShipping";
import InventoryIcon from "@mui/icons-material/Inventory";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { fetchDeliveries } from "@/services/api";

const STATUS_TABS = ["未配送", "配送中", "配送完了"] as const;
const STATUS_ICONS = {
  "未配送": <InventoryIcon />,
  "配送中": <LocalShippingIcon />,
  "配送完了": <CheckCircleIcon />,
};
const STATUS_COLORS: Record<string, "default" | "info" | "success"> = {
  "未配送": "default",
  "配送中": "info",
  "配送完了": "success",
};

export default function DeliveriesPage() {
  const [tab, setTab] = useState(0);
  const currentStatus = STATUS_TABS[tab];

  const { data: deliveries, isLoading } = useQuery({
    queryKey: ["deliveries", currentStatus],
    queryFn: () => fetchDeliveries(currentStatus),
  });

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        配送状況
      </Typography>

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        {STATUS_TABS.map((s) => (
          <Tab key={s} label={s} icon={STATUS_ICONS[s]} iconPosition="start" />
        ))}
      </Tabs>

      {isLoading ? (
        <CircularProgress />
      ) : !deliveries?.length ? (
        <Alert severity="info">{currentStatus}の配送はありません</Alert>
      ) : (
        <Grid container spacing={2}>
          {deliveries.map((d) => (
            <Grid item xs={12} sm={6} md={4} key={d.delivery_id}>
              <Card data-testid={`delivery-card-${d.delivery_id}`}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      配送 #{d.delivery_id}
                    </Typography>
                    <Chip
                      label={d.status}
                      color={STATUS_COLORS[d.status] || "default"}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    店舗: {d.store_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    ドライバー: {d.driver_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    予定: {new Date(d.scheduled_at).toLocaleString("ja-JP")}
                  </Typography>
                  {d.completed_at && (
                    <Typography variant="body2" color="text.secondary">
                      完了: {new Date(d.completed_at).toLocaleString("ja-JP")}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
