import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import AuthProvider from "@/auth/AuthProvider";
import ErrorBoundary from "@/components/ErrorBoundary";
import Layout from "@/components/Layout";
import DashboardPage from "@/pages/DashboardPage";
import OrdersPage from "@/pages/OrdersPage";
import DeliveriesPage from "@/pages/DeliveriesPage";
import DriverPage from "@/pages/DriverPage";
import ConsentPage from "@/pages/ConsentPage";
import { useConsentStatus, useCurrentUser } from "@/hooks/useAuth";
import { CircularProgress, Box, Alert } from "@mui/material";
import { ROLE_MANAGER, ROLE_DRIVER } from "@/types";
import type { User } from "@/types";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 60 * 1000,
      refetchOnWindowFocus: false,
    },
  },
});

const theme = createTheme({
  palette: {
    primary: { main: "#0072B2" },
    secondary: { main: "#E69F00" },
  },
  typography: {
    fontFamily:
      '"Noto Sans JP", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

/** ロールベースのルート認可ガード */
function RoleGuard({
  user,
  allowedRoles,
  children,
}: {
  user: User | undefined;
  allowedRoles: string[];
  children: React.ReactNode;
}) {
  if (!user || !allowedRoles.some((r) => user.roles.includes(r))) {
    return <Alert severity="error">このページへのアクセス権限がありません</Alert>;
  }
  return <>{children}</>;
}

function AppRoutes() {
  const { data: user, isLoading: userLoading, error: userError } = useCurrentUser();
  const { data: consent, isLoading: consentLoading, error: consentError } = useConsentStatus();

  if (userLoading || consentLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress aria-label="読み込み中" />
      </Box>
    );
  }

  if (userError || consentError) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <Alert severity="error">データの取得に失敗しました。ページを再読み込みしてください。</Alert>
      </Box>
    );
  }

  // 同意未取得
  if (consent && !consent.consented) {
    return <ConsentPage policyVersion={consent.policy_version} />;
  }

  // デフォルトリダイレクト先
  const defaultPath = user?.roles.includes(ROLE_MANAGER)
    ? "/dashboard"
    : user?.roles.includes(ROLE_DRIVER)
      ? "/driver"
      : "/";

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route
          path="/dashboard"
          element={
            <RoleGuard user={user} allowedRoles={[ROLE_MANAGER]}>
              <DashboardPage />
            </RoleGuard>
          }
        />
        <Route
          path="/orders"
          element={
            <RoleGuard user={user} allowedRoles={[ROLE_MANAGER]}>
              <OrdersPage />
            </RoleGuard>
          }
        />
        <Route
          path="/deliveries"
          element={
            <RoleGuard user={user} allowedRoles={[ROLE_MANAGER]}>
              <DeliveriesPage />
            </RoleGuard>
          }
        />
        <Route
          path="/driver"
          element={
            <RoleGuard user={user} allowedRoles={[ROLE_DRIVER]}>
              <DriverPage />
            </RoleGuard>
          }
        />
        <Route path="*" element={<Navigate to={defaultPath} replace />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <ErrorBoundary>
          <AuthProvider>
            <BrowserRouter>
              <AppRoutes />
            </BrowserRouter>
          </AuthProvider>
        </ErrorBoundary>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
