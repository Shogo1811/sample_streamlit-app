/** ユーザー情報 */
export interface User {
  user_id: string;
  roles: string[];
  store_id: number | null;
  driver_id: number | null;
}

/** 同意ステータス */
export interface ConsentStatus {
  consented: boolean;
  policy_version: string;
}

/** 食材マスタ */
export interface Ingredient {
  ingredient_id: number;
  ingredient_name: string;
  category: string;
  unit: string;
  threshold: number;
}

/** 在庫 */
export interface InventoryItem {
  store_id: number;
  ingredient_name: string;
  category: string;
  current_quantity: number;
  threshold: number;
  unit: string;
  updated_at: string;
}

/** 低在庫アイテム */
export interface LowStockItem {
  ingredient_name: string;
  category: string;
  current_quantity: number;
  threshold: number;
  unit: string;
}

/** 発注提案 */
export interface Proposal {
  proposal_id: number;
  ingredient_name: string;
  category: string;
  recommended_quantity: number;
  reason: string;
  status: string;
  created_at: string;
}

/** 承認済み発注予定 */
export interface OrderPlan {
  plan_id: number;
  ingredient_name: string;
  quantity: number;
  approved_by: string;
  approved_at: string;
}

/** 配送（店長向け） */
export interface Delivery {
  delivery_id: number;
  store_name: string;
  driver_name: string;
  status: string;
  scheduled_at: string;
  completed_at: string | null;
}

/** 配送（ドライバー向け） */
export interface DriverDelivery {
  delivery_id: number;
  store_name: string;
  status: string;
  scheduled_at: string;
}

/** SP 結果 */
export interface SPResult {
  success: boolean;
  message: string;
}

/** ロール定数 */
export const ROLE_MANAGER = "MANAGER";
export const ROLE_DRIVER = "DRIVER";
