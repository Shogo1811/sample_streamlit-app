import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
} from "@mui/material";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { fetchInventory, fetchLowStock, fetchCategories } from "@/services/api";
import LowStockAlert from "@/components/LowStockAlert";

const COLORS = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"];

export default function DashboardPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>("すべて");

  const { data: inventory, isLoading: invLoading, error: invError } = useQuery({
    queryKey: ["inventory"],
    queryFn: fetchInventory,
    refetchInterval: 5 * 60 * 1000,
  });

  const { data: lowStock } = useQuery({
    queryKey: ["low-stock"],
    queryFn: fetchLowStock,
    refetchInterval: 5 * 60 * 1000,
  });

  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: fetchCategories,
  });

  const filteredInventory = useMemo(() => {
    if (!inventory) return [];
    if (selectedCategory === "すべて") return inventory;
    return inventory.filter((item) => item.category === selectedCategory);
  }, [inventory, selectedCategory]);

  if (invLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (invError) {
    return <Alert severity="error">データの取得に失敗しました</Alert>;
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        在庫ダッシュボード
      </Typography>

      {lowStock && <LowStockAlert items={lowStock} />}

      <FormControl sx={{ mb: 3, minWidth: 200 }}>
        <InputLabel>カテゴリ</InputLabel>
        <Select
          value={selectedCategory}
          label="カテゴリ"
          onChange={(e) => setSelectedCategory(e.target.value)}
          data-testid="category-filter"
        >
          <MenuItem value="すべて">すべて</MenuItem>
          {categories?.map((cat) => (
            <MenuItem key={cat} value={cat}>
              {cat}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Typography variant="h6" gutterBottom>
        在庫数量
      </Typography>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={filteredInventory}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="ingredient_name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="current_quantity" name="現在数量" fill={COLORS[0]} />
          <Bar dataKey="threshold" name="閾値" fill={COLORS[1]} />
        </BarChart>
      </ResponsiveContainer>

      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
        在庫推移
      </Typography>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={filteredInventory}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="updated_at" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="current_quantity"
            name="数量"
            stroke={COLORS[0]}
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
}
