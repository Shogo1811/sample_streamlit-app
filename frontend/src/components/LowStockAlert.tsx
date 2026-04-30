import { Alert, AlertTitle, List, ListItem, ListItemText } from "@mui/material";
import type { LowStockItem } from "@/types";

interface Props {
  items: LowStockItem[];
}

export default function LowStockAlert({ items }: Props) {
  if (items.length === 0) return null;

  return (
    <Alert severity="warning" sx={{ mb: 2 }} data-testid="low-stock-alert">
      <AlertTitle>低在庫アラート（{items.length}件）</AlertTitle>
      <List dense>
        {items.map((item) => (
          <ListItem key={item.ingredient_name} disablePadding>
            <ListItemText
              primary={`${item.ingredient_name}（${item.category}）`}
              secondary={`現在: ${item.current_quantity}${item.unit} / 閾値: ${item.threshold}${item.unit}`}
            />
          </ListItem>
        ))}
      </List>
    </Alert>
  );
}
