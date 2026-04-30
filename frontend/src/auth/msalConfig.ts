import { Configuration, LogLevel, PublicClientApplication } from "@azure/msal-browser";

const TENANT_ID = import.meta.env.VITE_AZURE_AD_TENANT_ID || "";
const CLIENT_ID = import.meta.env.VITE_AZURE_AD_CLIENT_ID || "";

export const msalConfig: Configuration = {
  auth: {
    clientId: CLIENT_ID || "00000000-0000-0000-0000-000000000000",
    authority: `https://login.microsoftonline.com/${TENANT_ID || "common"}`,
    redirectUri: window.location.origin,
    postLogoutRedirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
  system: {
    loggerOptions: {
      logLevel: LogLevel.Warning,
    },
  },
};

export const loginRequest = {
  scopes: CLIENT_ID ? [`api://${CLIENT_ID}/access_as_user`] : [],
};

// Azure AD 未設定時はダミーインスタンス
export const msalInstance = new PublicClientApplication(msalConfig);
