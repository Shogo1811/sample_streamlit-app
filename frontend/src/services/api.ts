import axios from "axios";
import { InteractionRequiredAuthError } from "@azure/msal-browser";
import { msalInstance, loginRequest } from "@/auth/msalConfig";
import type {
  User,
  ConsentStatus,
  Ingredient,
  InventoryItem,
  LowStockItem,
  Proposal,
  OrderPlan,
  Delivery,
  DriverDelivery,
  SPResult,
} from "@/types";

const api = axios.create({
  baseURL: "/api",
});

// リクエストインターセプター: Bearer トークンを付与
const isDev = !import.meta.env.VITE_AZURE_AD_TENANT_ID;

api.interceptors.request.use(async (config) => {
  // DEVモード: Azure AD未設定時はトークンなしでリクエスト
  if (isDev) return config;

  const accounts = msalInstance.getAllAccounts();
  if (accounts.length > 0) {
    try {
      const response = await msalInstance.acquireTokenSilent({
        ...loginRequest,
        account: accounts[0],
      });
      config.headers.Authorization = `Bearer ${response.accessToken}`;
    } catch (error) {
      if (error instanceof InteractionRequiredAuthError) {
        await msalInstance.acquireTokenRedirect(loginRequest);
        throw error;
      }
      throw error;
    }
  }
  return config;
});

// --- Auth ---
export const fetchMe = () => api.get<User>("/auth/me").then((r) => r.data);
export const fetchConsentStatus = () =>
  api.get<ConsentStatus>("/auth/consent").then((r) => r.data);
export const postConsent = (policyVersion: string) =>
  api
    .post<ConsentStatus>("/auth/consent", { policy_version: policyVersion })
    .then((r) => r.data);
export const revokeConsent = () =>
  api.delete<ConsentStatus>("/auth/consent").then((r) => r.data);

// --- Inventory ---
export const fetchInventory = () =>
  api.get<InventoryItem[]>("/inventory").then((r) => r.data);
export const fetchLowStock = () =>
  api.get<LowStockItem[]>("/inventory/low-stock").then((r) => r.data);
export const fetchIngredients = () =>
  api.get<Ingredient[]>("/ingredients").then((r) => r.data);
export const fetchCategories = () =>
  api.get<string[]>("/ingredients/categories").then((r) => r.data);

// --- Orders ---
export const fetchProposals = (status?: string) =>
  api
    .get<Proposal[]>("/orders/proposals", { params: status ? { status } : {} })
    .then((r) => r.data);
export const approveProposal = (proposalId: number, quantity: number) =>
  api
    .post<SPResult>(`/orders/proposals/${proposalId}/approve`, { quantity })
    .then((r) => r.data);
export const rejectProposal = (proposalId: number) =>
  api
    .post<SPResult>(`/orders/proposals/${proposalId}/reject`)
    .then((r) => r.data);
export const fetchOrderPlans = () =>
  api.get<OrderPlan[]>("/orders/plans").then((r) => r.data);
export const executeOrderPlan = (planId: number) =>
  api
    .post<SPResult>(`/orders/plans/${planId}/execute`)
    .then((r) => r.data);

// --- Deliveries ---
export const fetchDeliveries = (status?: string) =>
  api
    .get<Delivery[]>("/deliveries", { params: status ? { status } : {} })
    .then((r) => r.data);
export const fetchMyDeliveries = () =>
  api.get<DriverDelivery[]>("/deliveries/mine").then((r) => r.data);
export const completeDelivery = (deliveryId: number) =>
  api
    .post<SPResult>(`/deliveries/${deliveryId}/complete`)
    .then((r) => r.data);
