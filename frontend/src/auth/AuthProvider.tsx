import {
  MsalProvider,
  AuthenticatedTemplate,
  UnauthenticatedTemplate,
  useMsal,
} from "@azure/msal-react";
import { Button, Box, Typography } from "@mui/material";
import { ReactNode } from "react";
import { msalInstance, loginRequest } from "./msalConfig";

function LoginButton() {
  const { instance } = useMsal();

  const handleLogin = () => {
    instance.loginRedirect(loginRequest);
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="100vh"
      gap={2}
    >
      <Typography variant="h4">ラーメン物流管理システム</Typography>
      <Typography color="text.secondary">
        ログインして続行してください
      </Typography>
      <Button variant="contained" size="large" onClick={handleLogin}>
        Azure AD でログイン
      </Button>
    </Box>
  );
}

interface AuthProviderProps {
  children: ReactNode;
}

export default function AuthProvider({ children }: AuthProviderProps) {
  return (
    <MsalProvider instance={msalInstance}>
      <AuthenticatedTemplate>{children}</AuthenticatedTemplate>
      <UnauthenticatedTemplate>
        <LoginButton />
      </UnauthenticatedTemplate>
    </MsalProvider>
  );
}
