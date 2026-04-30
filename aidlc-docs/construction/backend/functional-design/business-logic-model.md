# Backend 機能設計 — ビジネスロジックモデル

## API エンドポイント設計

### 認証・ユーザー
| Method | Path | 説明 | 認証 | ロール |
|---|---|---|---|---|
| GET | /api/auth/me | 現在のユーザー情報+ロール | 必須 | 全ロール |
| GET | /api/auth/consent | 同意ステータス確認 | 必須 | 全ロール |
| POST | /api/auth/consent | 同意記録 | 必須 | 全ロール |

### 在庫
| Method | Path | 説明 | 認証 | ロール |
|---|---|---|---|---|
| GET | /api/inventory | 在庫一覧（自店舗フィルタ） | 必須 | MANAGER |
| GET | /api/inventory/low-stock | 低在庫アイテム | 必須 | MANAGER |
| GET | /api/ingredients | 食材マスタ | 必須 | MANAGER |
| GET | /api/ingredients/categories | カテゴリ一覧 | 必須 | MANAGER |

### 発注
| Method | Path | 説明 | 認証 | ロール |
|---|---|---|---|---|
| GET | /api/orders/proposals | 発注提案一覧 | 必須 | MANAGER |
| POST | /api/orders/proposals/{id}/approve | 承認 | 必須 | MANAGER |
| POST | /api/orders/proposals/{id}/reject | 却下 | 必須 | MANAGER |
| GET | /api/orders/plans | 承認済み発注予定 | 必須 | MANAGER |
| POST | /api/orders/plans/{id}/execute | 発注実行 | 必須 | MANAGER |

### 配送
| Method | Path | 説明 | 認証 | ロール |
|---|---|---|---|---|
| GET | /api/deliveries | 配送一覧（店長向け） | 必須 | MANAGER |
| GET | /api/deliveries/mine | 自分の配送一覧（ドライバー） | 必須 | DRIVER |
| POST | /api/deliveries/{id}/complete | 配送完了報告 | 必須 | DRIVER |

---

## 認証フロー

```
1. Frontend: MSAL.js → Azure AD → access_token (JWT)
2. Frontend: Authorization: Bearer {access_token} → FastAPI
3. FastAPI AuthMiddleware:
   a. JWT 検証（Azure AD JWKS 公開鍵）
   b. claims から oid (user_id), groups[] を抽出
   c. groups → ロールマッピング（AD Group ID → MANAGER/DRIVER）
   d. ロール + related_id を request.state に設定
4. Router: Depends(require_role("MANAGER")) でロール検証
5. DAL: store_id / driver_id でデータフィルタリング（RLS 代替）
```

## ロールマッピング

Azure AD グループ → アプリロール:
```python
ROLE_GROUP_MAPPING = {
    "<MANAGER_GROUP_ID>": "MANAGER",
    "<DRIVER_GROUP_ID>": "DRIVER",
}
```
- 環境変数で設定: `AZURE_AD_MANAGER_GROUP_ID`, `AZURE_AD_DRIVER_GROUP_ID`
- ユーザーは複数グループに所属可能（MANAGER + DRIVER）

## データフィルタリング（RLS 代替）

現行の RLS は CURRENT_USER() でフィルタしていたが、サービスアカウント接続では全データが見える。
アプリ層で以下のフィルタを適用:

| ロール | フィルタ方式 |
|---|---|
| MANAGER | Azure AD oid → USER_ROLE_MAPPING.USER_ID → related_id (store_id) で在庫・発注をフィルタ |
| DRIVER | Azure AD oid → USER_ROLE_MAPPING.USER_ID → related_id (driver_id) で配送をフィルタ |

※ USER_ROLE_MAPPING テーブルは維持し、USER_ID を Azure AD oid に更新する

---

## Pydantic スキーマ

### リクエスト
- `ApproveProposalRequest`: quantity (int, 1-10000)

### レスポンス
- `UserResponse`: user_id, roles[], store_id?, driver_id?
- `ConsentStatusResponse`: consented (bool), policy_version
- `IngredientResponse`: ingredient_id, ingredient_name, category, unit, threshold
- `InventoryResponse`: store_id, ingredient_name, category, current_quantity, threshold, unit, updated_at
- `LowStockResponse`: ingredient_name, category, current_quantity, threshold, unit
- `ProposalResponse`: proposal_id, ingredient_name, category, recommended_quantity, reason, status, created_at
- `OrderPlanResponse`: plan_id, ingredient_name, quantity, approved_by, approved_at
- `DeliveryResponse`: delivery_id, store_name, driver_name?, status, scheduled_at, completed_at?
- `DriverDeliveryResponse`: delivery_id, store_name, status, scheduled_at
- `SPResultResponse`: success (bool), message (str)
